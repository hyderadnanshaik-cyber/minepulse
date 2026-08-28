"""
Infrastructure Assets API
GET  /api/infrastructure          - List all mine infrastructure assets
GET  /api/infrastructure/{id}     - Get single asset details
POST /api/infrastructure          - Add new infrastructure asset
PATCH /api/infrastructure/{id}    - Update asset status or coordinates
DELETE /api/infrastructure/{id}   - Decommission an asset

GIS endpoints:
GET  /api/gis/site                - Authoritative mine site location (Jharia)
GET  /api/gis/gateway             - Main Gateway / Raspberry Pi details + location
GET  /api/gis/infrastructure      - GeoJSON FeatureCollection of infrastructure
GET  /api/gis/impact              - Spatial intersection: infrastructure inside active risk zones
"""
import math
from typing import Dict, Any, List, Optional
from fastapi import APIRouter, Depends, HTTPException, Body
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, text, desc

from app.core.database import get_db
from app.auth.firebase_auth import get_current_user
from app.models.infrastructure import InfrastructureAsset, MineConfig
from app.models.gateway import Gateway
from app.models.ai_prediction import AIPrediction
from app.models.node import Node

router = APIRouter(prefix="/infrastructure", tags=["Infrastructure Assets"])

# ─────────────────────────── Haversine helper ────────────────────────────

def _haversine_m(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    R = 6371000.0
    phi1, phi2 = math.radians(lat1), math.radians(lat2)
    dlat = math.radians(lat2 - lat1)
    dlon = math.radians(lon2 - lon1)
    a = math.sin(dlat / 2) ** 2 + math.cos(phi1) * math.cos(phi2) * math.sin(dlon / 2) ** 2
    return R * 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))

# ─────────────────────────── CRUD Endpoints ──────────────────────────────

@router.get("")
async def list_infrastructure(
    asset_type: Optional[str] = None,
    status: Optional[str] = None,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user),
) -> List[Dict[str, Any]]:
    """Returns all mine infrastructure assets from PostgreSQL."""
    query = select(InfrastructureAsset).where(InfrastructureAsset.is_active == True)
    if asset_type:
        query = query.where(InfrastructureAsset.asset_type == asset_type.upper())
    if status:
        query = query.where(InfrastructureAsset.status == status.upper())
    result = await db.execute(query)
    assets = result.scalars().all()
    return [_serialize_asset(a) for a in assets]


@router.get("/{asset_id}")
async def get_infrastructure_asset(
    asset_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user),
) -> Dict[str, Any]:
    result = await db.execute(select(InfrastructureAsset).where(InfrastructureAsset.id == asset_id))
    asset = result.scalar_one_or_none()
    if not asset:
        raise HTTPException(status_code=404, detail="Infrastructure asset not found")
    return _serialize_asset(asset)


@router.post("", status_code=201)
async def create_infrastructure_asset(
    payload: Dict[str, Any] = Body(...),
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user),
) -> Dict[str, Any]:
    """Add a new mine infrastructure asset."""
    asset = InfrastructureAsset(
        name=payload["name"],
        asset_type=payload["asset_type"].upper(),
        latitude=payload.get("latitude"),
        longitude=payload.get("longitude"),
        status=payload.get("status", "OPERATIONAL").upper(),
        criticality=payload.get("criticality", "MEDIUM").upper(),
        description=payload.get("description"),
        is_active=True,
    )
    db.add(asset)
    await db.commit()
    await db.refresh(asset)
    return _serialize_asset(asset)


@router.patch("/{asset_id}")
async def update_infrastructure_asset(
    asset_id: int,
    payload: Dict[str, Any] = Body(...),
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user),
) -> Dict[str, Any]:
    result = await db.execute(select(InfrastructureAsset).where(InfrastructureAsset.id == asset_id))
    asset = result.scalar_one_or_none()
    if not asset:
        raise HTTPException(status_code=404, detail="Infrastructure asset not found")
    for field in ["name", "asset_type", "latitude", "longitude", "status", "criticality", "description"]:
        if field in payload:
            setattr(asset, field, payload[field])
    await db.commit()
    await db.refresh(asset)
    return _serialize_asset(asset)


@router.delete("/{asset_id}")
async def decommission_infrastructure_asset(
    asset_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user),
) -> Dict[str, Any]:
    result = await db.execute(select(InfrastructureAsset).where(InfrastructureAsset.id == asset_id))
    asset = result.scalar_one_or_none()
    if not asset:
        raise HTTPException(status_code=404, detail="Infrastructure asset not found")
    asset.is_active = False
    asset.status = "DECOMMISSIONED"
    await db.commit()
    return {"message": f"Asset '{asset.name}' decommissioned.", "id": asset_id}


# ─────────────────────────── GIS Impact Endpoints ────────────────────────

@router.get("/gis/site")
async def get_mine_site(
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user),
) -> Dict[str, Any]:
    """Returns the authoritative Jharia Coal Mine Site reference location."""
    result = await db.execute(
        select(MineConfig).where(MineConfig.key.in_(["MINE_SITE_LAT", "MINE_SITE_LON", "MINE_SITE_NAME"]))
    )
    configs = {c.key: c.value for c in result.scalars().all()}
    lat = configs.get("MINE_SITE_LAT")
    lon = configs.get("MINE_SITE_LON")
    name = configs.get("MINE_SITE_NAME", "Jharia Coalfield — SIH2026 Mine Site")
    if not lat or not lon:
        return {
            "configured": False,
            "message": "Mine site coordinates not configured. Set MINE_SITE_LAT and MINE_SITE_LON via the admin API.",
        }
    return {
        "configured": True,
        "name": name,
        "latitude": float(lat),
        "longitude": float(lon),
        "description": "Authoritative mine reference location. Source: Jharia Coalfield, Jharkhand, India.",
        "geojson": {
            "type": "Feature",
            "geometry": {"type": "Point", "coordinates": [float(lon), float(lat)]},
            "properties": {"name": name, "type": "MINE_SITE"},
        },
    }


@router.get("/gis/gateway")
async def get_gateway_gis(
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user),
) -> Dict[str, Any]:
    """Returns Main Gateway (Raspberry Pi) GIS location and telemetry."""
    result = await db.execute(select(Gateway).order_by(Gateway.id).limit(1))
    gw = result.scalar_one_or_none()
    if not gw:
        return {"configured": False, "message": "No gateway record found in database."}
    if gw.latitude is None or gw.longitude is None:
        return {
            "configured": False,
            "id": gw.id,
            "name": gw.name,
            "device": "Raspberry Pi Gateway",
            "device_id": gw.device_id,
            "status": gw.status,
            "message": "Gateway location not configured. Set latitude and longitude in the gateway record.",
        }
    return {
        "configured": True,
        "id": gw.id,
        "name": "Main Gateway — Raspberry Pi",
        "display_label": "Main Gateway",
        "device": "Raspberry Pi Zero 2 W",
        "device_id": gw.device_id,
        "ip_address": gw.ip_address,
        "latitude": gw.latitude,
        "longitude": gw.longitude,
        "status": gw.status or "UNKNOWN",
        "cpu_usage": gw.cpu_usage,
        "ram_usage": gw.ram_usage,
        "temperature_c": gw.temperature,
        "mqtt_status": gw.mqtt_status,
        "mesh_status": gw.mesh_status,
        "internet_connected": gw.internet_connected,
        "last_seen": gw.last_seen.isoformat() if gw.last_seen else None,
        "geojson": {
            "type": "Feature",
            "geometry": {"type": "Point", "coordinates": [gw.longitude, gw.latitude]},
            "properties": {
                "name": "Main Gateway — Raspberry Pi",
                "type": "GATEWAY",
                "status": gw.status,
                "device_id": gw.device_id,
            },
        },
    }


@router.get("/gis/infrastructure")
async def get_infrastructure_geojson(
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user),
) -> Dict[str, Any]:
    """Returns GeoJSON FeatureCollection of all active infrastructure assets."""
    result = await db.execute(
        select(InfrastructureAsset).where(
            InfrastructureAsset.is_active == True,
            InfrastructureAsset.latitude.isnot(None),
            InfrastructureAsset.longitude.isnot(None),
        )
    )
    assets = result.scalars().all()
    features = []
    for a in assets:
        features.append({
            "type": "Feature",
            "geometry": {"type": "Point", "coordinates": [a.longitude, a.latitude]},
            "properties": {
                "id": a.id,
                "name": a.name,
                "asset_type": a.asset_type,
                "status": a.status,
                "criticality": a.criticality,
                "description": a.description,
            },
        })
    return {"type": "FeatureCollection", "features": features}


@router.get("/gis/impact")
async def get_infrastructure_impact(
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user),
) -> Dict[str, Any]:
    """
    Spatial intersection engine:
    1. Finds all nodes currently in HIGH or CRITICAL risk state.
    2. Computes their predicted affected zone (centroid + radius from risk score).
    3. Queries all infrastructure assets.
    4. Returns assets inside or within 100m of the affected zone.
    Relationship is derived from spatial distance — never hardcoded.
    """
    # 1. Get latest predictions per node
    preds_res = await db.execute(
        select(AIPrediction).order_by(desc(AIPrediction.id)).limit(200)
    )
    preds = preds_res.scalars().all()
    pred_map: Dict[str, AIPrediction] = {}
    for p in preds:
        if p.node_id_fk not in pred_map:
            pred_map[p.node_id_fk] = p

    # 2. Collect anomalous nodes with coordinates
    nodes_res = await db.execute(
        select(Node).where(Node.latitude.isnot(None), Node.longitude.isnot(None))
    )
    all_nodes = nodes_res.scalars().all()

    hazard_nodes = []
    for node in all_nodes:
        pred = pred_map.get(node.node_id)
        if pred and pred.risk_score and pred.risk_score >= 50.0:
            hazard_nodes.append({
                "node_id": node.node_id,
                "name": node.name or node.node_id,
                "lat": float(node.latitude),
                "lon": float(node.longitude),
                "risk_score": float(pred.risk_score),
                "risk_level": pred.risk_level or "HIGH",
            })

    if not hazard_nodes:
        return {
            "hazard_active": False,
            "affected_nodes": [],
            "predicted_zone": None,
            "affected_infrastructure": [],
            "message": "No active high-risk nodes. Infrastructure is not currently predicted to be at risk.",
        }

    # 3. Compute centroid and dynamic radius from risk scores
    avg_lat = sum(n["lat"] for n in hazard_nodes) / len(hazard_nodes)
    avg_lon = sum(n["lon"] for n in hazard_nodes) / len(hazard_nodes)
    max_risk = max(n["risk_score"] for n in hazard_nodes)

    # Geotechnical Subsidence Influence Zone:
    # Based on depth of cover (~120m) and angle of draw (35° to 45°), the surface strain zone
    # extends dynamically from 150m (moderate risk) up to 450m (critical collapse)
    zone_radius_m = 150.0 + ((max_risk - 50.0) / 50.0) * 300.0
    zone_radius_m = max(150.0, min(500.0, zone_radius_m))

    # 4. Query all active public infrastructure assets
    infra_res = await db.execute(
        select(InfrastructureAsset).where(
            InfrastructureAsset.is_active == True,
            InfrastructureAsset.latitude.isnot(None),
            InfrastructureAsset.longitude.isnot(None),
        )
    )
    all_infra = infra_res.scalars().all()

    # 5. Intersect: find assets within zone_radius_m of hazard centroid
    affected = []
    for a in all_infra:
        dist_m = _haversine_m(avg_lat, avg_lon, float(a.latitude), float(a.longitude))
        if dist_m <= zone_radius_m:
            # Impact severity based on distance and asset criticality
            proximity_ratio = 1.0 - (dist_m / zone_radius_m)
            impact_level = "CRITICAL" if (proximity_ratio > 0.5 or a.criticality == "CRITICAL") else ("HIGH" if proximity_ratio > 0.25 else "MEDIUM")

            # Tailor reason specifically to asset type
            type_action = {
                "HIGHWAY": "Risk of pavement fissure and sinkhole. Mandatory highway traffic diversion required.",
                "RESIDENTIAL_AREA": "Foundation shear and structural cracking risk. Precautionary evacuation of residents advised.",
                "WATER_SUPPLY": "Risk of high-pressure pipe rupture and flooding. Isolate municipal water pump main.",
                "RAILWAY": "Rail track alignment distortion risk. Impose speed restriction / halt freight siding operations.",
                "POWER_GRID": "Transformer foundation tilt hazard. Switch feeder to backup grid substation.",
                "SCHOOL": "High civilian safety risk. Order immediate evacuation of students and staff.",
                "HOSPITAL": "Designated emergency facility. Put trauma ward on high alert and secure medical gas lines.",
            }.get(a.asset_type, "Located within predicted ground strain perimeter.")

            affected.append({
                "id": a.id,
                "name": a.name,
                "asset_type": a.asset_type,
                "latitude": float(a.latitude),
                "longitude": float(a.longitude),
                "criticality": a.criticality,
                "status": a.status,
                "impact_level": impact_level,
                "distance_from_zone_center_m": round(dist_m, 1),
                "reason": f"{type_action} (Located {round(dist_m, 0):.0f}m from sinking hazard; Risk: {max_risk:.0f}/100; Sinking station: {', '.join(n['node_id'] for n in hazard_nodes)}).",
            })

    # Sort by distance ascending
    affected.sort(key=lambda x: x["distance_from_zone_center_m"])

    evacuation_recommended = max_risk >= 70.0 or any(a["criticality"] == "CRITICAL" for a in affected)

    return {
        "hazard_active": True,
        "affected_nodes": hazard_nodes,
        "predicted_zone": {
            "centroid_lat": round(avg_lat, 7),
            "centroid_lon": round(avg_lon, 7),
            "radius_m": round(zone_radius_m, 1),
            "max_risk_score": round(max_risk, 1),
        },
        "affected_infrastructure_count": len(affected),
        "affected_infrastructure": affected,
        "evacuation_recommended": evacuation_recommended,
        "evacuation_level": "IMMEDIATE" if max_risk >= 75.0 else ("HIGH" if max_risk >= 55.0 else "ELEVATED"),
        "recommendation": (
            "IMMEDIATE PUBLIC EVACUATION & HIGHWAY CLOSURE: Divert traffic from NH-218 and evacuate civilian residents within risk perimeter immediately."
            if max_risk >= 75.0 else
            "RESTRICT ACCESS & DIVERT TRAFFIC: Place NH-218 and adjacent colonies on high watch. Prepare public evacuation routes."
        ),
    }


# ─────────────────────────── Serializer ─────────────────────────────────

def _serialize_asset(a: InfrastructureAsset) -> Dict[str, Any]:
    return {
        "id": a.id,
        "name": a.name,
        "asset_type": a.asset_type,
        "latitude": a.latitude,
        "longitude": a.longitude,
        "status": a.status,
        "criticality": a.criticality,
        "description": a.description,
        "is_active": a.is_active,
        "created_at": a.created_at.isoformat() if a.created_at else None,
        "updated_at": a.updated_at.isoformat() if a.updated_at else None,
    }

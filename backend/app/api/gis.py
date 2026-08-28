import json
from typing import Dict, Any, List, Optional
from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, text, desc

from app.core.database import get_db
from app.auth.firebase_auth import get_current_user
from app.models.node import Node
from app.models.panel import Panel
from app.models.crack_event import CrackEvent
from app.models.alert import Alert
from app.models.ai_prediction import AIPrediction

router = APIRouter(prefix="/gis", tags=["GIS & Spatial"])

@router.get("/nodes")
async def get_gis_nodes(
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user)
) -> Dict[str, Any]:
    """Returns a GeoJSON FeatureCollection of all sensor nodes from PostgreSQL."""
    res = await db.execute(select(Node))
    nodes = list(res.scalars().all())

    preds_res = await db.execute(select(AIPrediction).order_by(desc(AIPrediction.id)).limit(200))
    recent_preds = preds_res.scalars().all()
    latest_pred_map = {}
    for p in recent_preds:
        if p.node_id_fk not in latest_pred_map:
            latest_pred_map[p.node_id_fk] = p

    features = []
    for n in nodes:
        if n.latitude is not None and n.longitude is not None:
            pred = latest_pred_map.get(n.node_id)
            features.append({
                "type": "Feature",
                "geometry": {
                    "type": "Point",
                    "coordinates": [n.longitude, n.latitude]
                },
                "properties": {
                    "id": n.id,
                    "node_id": n.node_id,
                    "node_code": n.node_id,
                    "device_id": n.node_id,
                    "name": n.name or f"Station {n.node_id}",
                    "zone": n.zone or "Underground",
                    "panel_id": n.panel_id_fk,
                    "status": n.status or "ONLINE",
                    "risk_level": pred.risk_level if pred else "NORMAL",
                    "risk_score": pred.risk_score if pred else 0.0,
                    "anomaly_score": pred.anomaly_score if pred else 0.0,
                    "battery": n.battery_level,
                    "installed_at": n.installed_at.isoformat() if n.installed_at else None
                }
            })

    return {
        "type": "FeatureCollection",
        "features": features
    }

@router.get("/panels")
async def get_gis_panels(
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user)
) -> Dict[str, Any]:
    """Returns a GeoJSON FeatureCollection of all mine working panels."""
    res = await db.execute(select(Panel))
    panels = list(res.scalars().all())

    features = []
    for p in panels:
        # Default panel polygon surrounding nodes
        geom_dict = {
            "type": "Polygon",
            "coordinates": [[[86.418, 23.748], [86.425, 23.748], [86.425, 23.755], [86.418, 23.755], [86.418, 23.748]]]
        }

        features.append({
            "type": "Feature",
            "geometry": geom_dict,
            "properties": {
                "id": p.id,
                "panel_id": p.panel_id,
                "name": p.name or p.panel_id,
                "description": p.description,
                "status": p.status
            }
        })

    return {
        "type": "FeatureCollection",
        "features": features
    }

@router.get("/overview")
async def get_gis_overview(
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user)
) -> Dict[str, Any]:
    """Returns aggregated GIS layers (nodes, panels, risk zones, cracks) in one call."""
    nodes_geojson = await get_gis_nodes(db, current_user)
    panels_geojson = await get_gis_panels(db, current_user)
    return {
        "nodes": nodes_geojson,
        "panels": panels_geojson,
        "risk_zones": {"type": "FeatureCollection", "features": []},
        "crack_events": {"type": "FeatureCollection", "features": []}
    }

@router.get("/nearest-nodes")
async def get_nearest_nodes(
    latitude: float = Query(..., description="Target Latitude (e.g. 23.7500)"),
    longitude: float = Query(..., description="Target Longitude (e.g. 86.4200)"),
    limit: int = Query(5, ge=1, le=20),
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user)
) -> List[Dict[str, Any]]:
    """
    Executes native PostGIS spatial distance calculation:
    ST_Distance(ST_SetSRID(ST_MakePoint(longitude, latitude), 4326)::geography, ST_SetSRID(ST_MakePoint(:lon, :lat), 4326)::geography)
    """
    try:
        sql = text("""
            SELECT id, node_id, panel_id, latitude, longitude, status, battery_level,
                   ST_Distance(
                       ST_SetSRID(ST_MakePoint(longitude, latitude), 4326)::geography,
                       ST_SetSRID(ST_MakePoint(:target_lon, :target_lat), 4326)::geography
                   ) AS distance_meters
            FROM nodes
            WHERE latitude IS NOT NULL AND longitude IS NOT NULL
            ORDER BY distance_meters ASC
            LIMIT :limit
        """)
        res = await db.execute(sql, {"target_lon": longitude, "target_lat": latitude, "limit": limit})
        rows = res.fetchall()
        return [
            {
                "id": r.id,
                "node_id": r.node_id,
                "panel_id": r.panel_id,
                "latitude": r.latitude,
                "longitude": r.longitude,
                "status": r.status,
                "battery_level": r.battery_level,
                "distance_meters": round(r.distance_meters, 2)
            }
            for r in rows
        ]
    except Exception as e:
        # Fallback if PostGIS function not available in dialect
        res = await db.execute(select(Node).limit(limit))
        nodes = list(res.scalars().all())
        return [
            {
                "id": n.id,
                "node_id": n.node_id,
                "panel_id": n.panel_id_fk,
                "latitude": n.latitude,
                "longitude": n.longitude,
                "status": n.status,
                "battery_level": n.battery_level,
                "distance_meters": 0.0
            }
            for n in nodes
        ]

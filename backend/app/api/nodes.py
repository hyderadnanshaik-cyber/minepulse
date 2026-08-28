from typing import List, Optional, Dict, Any
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.auth.firebase_auth import get_current_user, require_role
from app.models.node import Node
from app.models.ai_prediction import AIPrediction
from sqlalchemy import select, desc
from app.schemas.node import (
    NodeResponse, NodeDetailResponse, NodeCreate, NodeRegisterRequest,
    NodeUpdate, NodeSummaryResponse, RegistrationCodeCreate, RegistrationCodeResponse
)
from app.services.node_service import NodeService
from app.mqtt.client import mqtt_client

router = APIRouter(prefix="/nodes", tags=["Nodes"])

@router.get("/summary", response_model=NodeSummaryResponse)
async def get_nodes_summary(
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Calculates live fleet summary cards (Total, Online, Warning, Critical, Offline) from PostgreSQL."""
    summary = await NodeService.get_node_summary(db)
    return summary

@router.get("", response_model=List[Dict[str, Any]])
async def list_nodes(
    panel_id: Optional[str] = None,
    status: Optional[str] = None,
    include_archived: bool = Query(False),
    skip: int = Query(0, ge=0),
    limit: int = Query(200, ge=1, le=500),
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """List all mine sensor nodes from PostgreSQL with dynamic risk levels."""
    nodes = await NodeService.get_nodes(
        db=db,
        panel_id=panel_id,
        status_filter=status,
        include_archived=include_archived,
        skip=skip,
        limit=limit
    )
    return nodes

@router.post("", status_code=status.HTTP_201_CREATED)
async def create_new_node(
    payload: NodeCreate,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(require_role("OPERATOR", "ADMIN", "ENGINEER"))
):
    """Onboarding Wizard: Create and persist a new monitoring node in PostgreSQL."""
    node = await NodeService.create_node(db, payload)
    return node

@router.get("/{node_id}")
async def get_node_detail(
    node_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Retrieve detailed information for a specific sensor node from PostgreSQL."""
    if node_id.isdigit():
        node = await NodeService.get_node_by_id(db, int(node_id))
    else:
        node = await NodeService.get_node_by_code(db, node_id)

    if not node:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Node not found")
    
    pred_res = await db.execute(
        select(AIPrediction).where(AIPrediction.node_id_fk == node.node_id).order_by(desc(AIPrediction.id)).limit(1)
    )
    pred = pred_res.scalar_one_or_none()

    return {
        "id": node.id,
        "node_id": node.node_id,
        "node_code": node.node_id,
        "device_id": node.node_id,
        "name": node.name or f"Station {node.node_id}",
        "zone": node.zone or "North Shaft",
        "site_id": node.site_id or "MINE-CENTRAL-01",
        "panel_id": node.panel_id_fk or "PANEL-A",
        "connection_type": node.connection_type or "LoRa",
        "gateway_id": node.gateway_id or "MINEGATE-01",
        "sensor_types": node.sensor_types or ["Displacement", "Tilt", "Crack", "Temperature", "Vibration"],
        "thresholds": node.thresholds or {
            "warning_disp_mm": 15.0, "critical_disp_mm": 25.0,
            "warning_tilt_deg": 2.0, "critical_tilt_deg": 3.5,
            "warning_crack_mm": 1.5, "critical_crack_mm": 3.0
        },
        "latitude": node.latitude,
        "longitude": node.longitude,
        "status": "ARCHIVED" if node.is_archived else (node.status or "ONLINE"),
        "risk_level": pred.risk_level if pred else "NORMAL",
        "risk_score": pred.risk_score if pred else 0.0,
        "battery_level": node.battery_level,
        "battery": node.battery_level,
        "signal_strength": node.signal_strength or -70.0,
        "is_archived": node.is_archived or False,
        "installed_at": node.installed_at.isoformat() if node.installed_at else None,
        "last_seen": node.updated_at.isoformat() if node.updated_at else (node.installed_at.isoformat() if node.installed_at else None)
    }

@router.patch("/{node_id}")
async def update_node_metadata(
    node_id: str,
    payload: NodeUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(require_role("OPERATOR", "ADMIN", "ENGINEER"))
):
    """Update node settings, location coordinates, and metadata in PostgreSQL."""
    node = await NodeService.update_node(db, node_id, payload)
    return node

@router.post("/{node_id}/archive")
async def archive_node_station(
    node_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(require_role("OPERATOR", "ADMIN", "ENGINEER"))
):
    """Soft-archive a node station without deleting historical telemetry for audit compliance."""
    result = await NodeService.archive_node(db, node_id)
    return result

@router.post("/register")
async def register_node(
    payload: NodeRegisterRequest,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Pair and register a new hardware node in PostgreSQL using a 6-digit pairing code."""
    node = await NodeService.register_node(db, payload)
    return node

@router.post("/registration-codes", response_model=RegistrationCodeResponse)
async def generate_registration_code(
    payload: RegistrationCodeCreate,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(require_role("ADMIN", "ENGINEER"))
):
    """Generate a new 6-digit node pairing code."""
    reg_code = await NodeService.generate_registration_code(db, payload)
    return reg_code

@router.post("/{node_id}/locate")
async def locate_node(
    node_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(require_role("OPERATOR", "ADMIN", "ENGINEER"))
):
    """Trigger physical buzzer and LED locator beacon on the node station."""
    if node_id.isdigit():
        node = await NodeService.get_node_by_id(db, int(node_id))
    else:
        node = await NodeService.get_node_by_code(db, node_id)

    if not node:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Node not found")

    topic = "minegate/MINEGATE-01/commands"
    payload = {"command": "LOCATE_NODE", "target_node": node.node_id, "duration_seconds": 15}
    success = mqtt_client.publish(topic, payload)

    return {
        "status": "SUCCESS" if success else "QUEUED",
        "message": f"Locate signal broadcasted to {node.node_id}. Buzzer and LED active.",
        "node_id": node.node_id
    }

@router.get("/{node_id}/history")
async def get_node_reading_history(
    node_id: str,
    limit: int = Query(100, ge=1, le=1000),
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Get time-series historical sensor readings for a node from PostgreSQL."""
    readings = await NodeService.get_node_readings(db, node_id, limit=limit)
    return readings

@router.get("/{node_id}/alerts")
async def get_node_alerts(
    node_id: str,
    limit: int = Query(50, ge=1, le=200),
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Get all alerts associated with a specific node from PostgreSQL."""
    alerts = await NodeService.get_node_alerts(db, node_id, limit=limit)
    return alerts

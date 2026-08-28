from typing import List, Any, Dict
from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.auth.firebase_auth import get_current_user
from app.schemas.telemetry import SensorReadingResponse, TelemetryIngestPayload
from app.services.telemetry_service import TelemetryService

router = APIRouter(prefix="/telemetry", tags=["Telemetry"])

@router.get("", response_model=List[Dict[str, Any]])
async def get_latest_telemetry(
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Retrieve the latest telemetry readings for all mine nodes."""
    return await TelemetryService.get_latest_readings_all_nodes(db)

@router.get("/{node_id}", response_model=List[SensorReadingResponse])
async def get_node_telemetry(
    node_id: str,
    limit: int = Query(100, ge=1, le=1000),
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Retrieve time-series readings for a given node."""
    return await TelemetryService.get_node_telemetry_history(db, node_id, limit=limit)

@router.post("/ingest", response_model=SensorReadingResponse)
async def ingest_telemetry_reading(
    payload: TelemetryIngestPayload,
    db: AsyncSession = Depends(get_db)
):
    """Internal HTTP ingest endpoint for sensor readings (MQTT or gateway webhook)."""
    reading = await TelemetryService.ingest_reading(db, payload)
    return reading

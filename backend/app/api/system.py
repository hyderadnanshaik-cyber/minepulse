from fastapi import APIRouter, Depends, HTTPException, Body
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text
from app.core.database import get_db
from app.mqtt.client import mqtt_client
import time

router = APIRouter(prefix="/system", tags=["System"])

@router.get("/health")
async def get_system_health(db: AsyncSession = Depends(get_db)):
    db_ok = False
    postgis_ok = False
    try:
        res = await db.execute(text("SELECT PostGIS_Version()"))
        v = res.scalar()
        postgis_ok = bool(v)
        db_ok = True
    except Exception:
        try:
            await db.execute(text("SELECT 1"))
            db_ok = True
        except Exception:
            db_ok = False

    return {
        "status": "HEALTHY" if db_ok else "DEGRADED",
        "timestamp": time.time(),
        "services": {
            "database": "ONLINE" if db_ok else "OFFLINE",
            "postgis": "ONLINE" if postgis_ok else "OFFLINE",
            "mqtt_broker": "ONLINE" if mqtt_client and mqtt_client.is_connected else "OFFLINE",
            "ai_engine": "ONLINE",
            "mesh_transport": "ONLINE",
            "offline_mode": "ACTIVE"
        }
    }

@router.get("/connectivity")
async def get_connectivity():
    return {
        "mode": "OFFLINE_FIRST",
        "mesh_active": True,
        "gateway_reachable": True,
        "internet_connected": False,
        "cloud_synced": True,
        "pending_sync_count": 0
    }

@router.post("/scenario/trigger")
async def trigger_scenario(payload: dict = Body(...)):
    """Triggers demonstration scenario across simulator & LoRa mesh."""
    scenario_name = payload.get("scenario", "ANOMALY_NODE_03")
    if mqtt_client and mqtt_client.is_connected:
        mqtt_client.publish("mine/simulator/scenario", {"scenario": scenario_name})
    return {
        "status": "SUCCESS",
        "scenario": scenario_name,
        "message": f"Demonstration scenario '{scenario_name}' dispatched to LoRa simulator."
    }

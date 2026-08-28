import json
import logging
from datetime import datetime, timezone
from typing import Dict, Any
from app.core.database import AsyncSessionLocal
from app.schemas.telemetry import TelemetryIngestPayload
from app.schemas.alert import AlertCreate
from app.services.telemetry_service import TelemetryService
from app.services.node_service import NodeService
from app.services.alert_service import AlertService
from app.services.mesh_service import MeshService
from app.services.gateway_service import GatewayService

logger = logging.getLogger(__name__)

def parse_naive_datetime(ts_val: Any) -> datetime:
    """Returns a naive datetime compatible with PostgreSQL TIMESTAMP WITHOUT TIME ZONE."""
    if isinstance(ts_val, (int, float)):
        dt = datetime.fromtimestamp(ts_val, tz=timezone.utc)
        return dt.replace(tzinfo=None)
    elif isinstance(ts_val, str):
        try:
            dt = datetime.fromisoformat(ts_val)
            return dt.replace(tzinfo=None)
        except Exception:
            return datetime.now()
    return datetime.now()

async def handle_telemetry(node_identifier: str, payload: Dict[str, Any]):
    """Processes incoming sensor telemetry data from MQTT into PostgreSQL."""
    try:
        async with AsyncSessionLocal() as db:
            parsed_time = parse_naive_datetime(payload.get("timestamp") or payload.get("recorded_at"))
            
            # Map full final hardware payload
            ingest_data = TelemetryIngestPayload(
                node_code=node_identifier if not node_identifier.startswith("DEV-") else None,
                device_id=node_identifier if node_identifier.startswith("DEV-") else payload.get("device_id"),
                node_id=node_identifier,
                gateway_id=payload.get("gateway_id", "MINEGATE-01"),
                recorded_at=parsed_time,
                timestamp=parsed_time,
                # MPU9250 9-Axis
                tilt=payload.get("tilt"),
                tilt_x=payload.get("tilt_x") if payload.get("tilt_x") is not None else payload.get("tilt"),
                tilt_y=payload.get("tilt_y"),
                vibration=payload.get("vibration"),
                accel_x=payload.get("accel_x"),
                accel_y=payload.get("accel_y"),
                accel_z=payload.get("accel_z", 1.0),
                gyro_x=payload.get("gyro_x"),
                gyro_y=payload.get("gyro_y"),
                gyro_z=payload.get("gyro_z"),
                mag_x=payload.get("mag_x"),
                mag_y=payload.get("mag_y"),
                mag_z=payload.get("mag_z"),
                # BME280 Environment
                temperature=payload.get("temperature"),
                humidity=payload.get("humidity"),
                pressure=payload.get("pressure"),
                # Ground Displacement
                displacement=payload.get("displacement"),
                displacement_rate=payload.get("displacement_rate"),
                displacement_baseline=payload.get("displacement_baseline"),
                # Potentiometric Crack Gauge
                crack_detected=payload.get("crack_detected") or payload.get("crack_status", False),
                crack_status=payload.get("crack_status", False),
                crack_width=payload.get("crack_width"),
                # Power
                battery_level=payload.get("battery_level") or payload.get("battery"),
                battery=payload.get("battery"),
                # IN865 LoRa & Mesh
                signal_strength=payload.get("signal_strength") or payload.get("rssi"),
                rssi=payload.get("rssi") or payload.get("signal_strength"),
                snr=payload.get("snr"),
                frequency_mhz=payload.get("frequency_mhz", 865.2),
                spreading_factor=payload.get("spreading_factor", 7),
                hop_count=payload.get("hop_count", 1),
                parent_node_id=payload.get("parent_node_id"),
                route=payload.get("route") or payload.get("mesh_route"),
                latitude=payload.get("latitude"),
                longitude=payload.get("longitude"),
                raw_payload=payload
            )
            await TelemetryService.ingest_reading(db, ingest_data)
    except Exception as e:
        logger.error(f"Error handling MQTT telemetry for {node_identifier}: {e}", exc_info=True)

async def handle_status(node_identifier: str, payload: Dict[str, Any]):
    """Processes heartbeat/status updates from nodes in PostgreSQL."""
    try:
        async with AsyncSessionLocal() as db:
            node = await NodeService.get_node_by_code(db, node_identifier)
            if node:
                node.status = payload.get("status", "ONLINE").upper()
                if "battery" in payload or "battery_level" in payload:
                    node.battery_level = payload.get("battery_level") or payload.get("battery")
                if "hop_count" in payload:
                    node.hop_count = payload.get("hop_count")
                if "parent_node_id" in payload:
                    node.parent_node_id = payload.get("parent_node_id")
                if "rssi" in payload or "signal_strength" in payload:
                    node.signal_strength = payload.get("rssi") or payload.get("signal_strength")
                node.installed_at = datetime.now()
                await db.commit()
    except Exception as e:
        logger.error(f"Error handling MQTT status for {node_identifier}: {e}")

async def handle_alert(node_identifier: str, payload: Dict[str, Any]):
    """Processes critical alert events published directly by hardware nodes into PostgreSQL."""
    try:
        async with AsyncSessionLocal() as db:
            alert_create = AlertCreate(
                node_id=node_identifier,
                alert_type=payload.get("alert_type", "HARDWARE_TRIGGERED_ALERT"),
                severity=payload.get("severity", "CRITICAL").upper(),
                title=payload.get("title", f"Hardware Alert from {node_identifier}"),
                message=payload.get("message", "Immediate subsidence or threshold trip detected."),
                risk_score=payload.get("risk_score", 85.0),
                local_alarm_activated=payload.get("local_alarm_activated", True)
            )
            await AlertService.create_alert(db, alert_create)
    except Exception as e:
        logger.error(f"Error handling MQTT alert for {node_identifier}: {e}")

async def handle_mesh(node_identifier: str, payload: Dict[str, Any]):
    """Processes mesh topology neighbor reports from nodes into PostgreSQL."""
    try:
        async with AsyncSessionLocal() as db:
            neighbors = payload.get("neighbors", [])
            route = payload.get("route", [node_identifier])
            hop_count = payload.get("hop_count", len(route))
            parent_id = payload.get("parent_node_id")

            await MeshService.update_mesh_connections(
                db=db,
                node_id_str=node_identifier,
                neighbors=neighbors,
                route_path=route,
                hop_count=hop_count,
                parent_node_id=parent_id
            )
    except Exception as e:
        logger.error(f"Error handling MQTT mesh update for {node_identifier}: {e}")

async def handle_gateway_status(payload: Dict[str, Any]):
    """Processes gateway hardware status messages into PostgreSQL."""
    try:
        async with AsyncSessionLocal() as db:
            await GatewayService.update_gateway_metrics(
                db=db,
                cpu_usage=payload.get("cpu_usage"),
                ram_usage=payload.get("ram_usage"),
                temperature=payload.get("temperature"),
                storage_used=payload.get("storage_used"),
                mqtt_status="ONLINE",
                mesh_status=payload.get("mesh_status", "ONLINE"),
                internet_connected=payload.get("internet_connected", True)
            )
    except Exception as e:
        logger.error(f"Error handling MQTT gateway status: {e}")

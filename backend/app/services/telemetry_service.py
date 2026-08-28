from datetime import datetime, timezone
from typing import List, Optional, Dict, Any
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, desc, func
from fastapi import HTTPException, status

from app.models.node import Node
from app.models.sensor_reading import SensorReading
from app.models.crack_event import CrackEvent
from app.schemas.telemetry import TelemetryIngestPayload
from app.services.ai_service import AIService
from app.ws.manager import ws_manager

class TelemetryService:

    @staticmethod
    async def ingest_reading(
        db: AsyncSession,
        payload: TelemetryIngestPayload
    ) -> SensorReading:
        raw_ts = payload.recorded_at or payload.timestamp
        if isinstance(raw_ts, str):
            try:
                now = datetime.fromisoformat(raw_ts.replace("Z", "+00:00"))
            except Exception:
                now = datetime.now()
        elif isinstance(raw_ts, datetime):
            now = raw_ts
        else:
            now = datetime.now()

        if hasattr(now, "tzinfo") and now.tzinfo is not None:
            now = now.replace(tzinfo=None)
        
        # 1. Resolve Node Identifier
        node_id_str = payload.node_id or payload.node_code or payload.device_id or "NODE_01"
        
        # Check if node exists in PostgreSQL
        node_res = await db.execute(select(Node).where(Node.node_id == node_id_str))
        node = node_res.scalar_one_or_none()

        hop_val = payload.hop_count or (len(payload.route) if payload.route else 1)
        parent_val = payload.parent_node_id or (payload.route[-2] if payload.route and len(payload.route) > 1 else None)
        rssi_val = payload.rssi if payload.rssi is not None else (payload.signal_strength if payload.signal_strength is not None else -70.0)

        if not node:
            node = Node(
                node_id=node_id_str,
                panel_id_fk="PANEL-A",
                latitude=payload.latitude or 23.7500,
                longitude=payload.longitude or 86.4200,
                status="ONLINE",
                battery_level=payload.battery_level or payload.battery or 100.0,
                installed_at=now,
                hardware_spec="ESP32+MPU9250+BME280+ADS1115+IN865",
                parent_node_id=parent_val,
                hop_count=hop_val,
                mesh_route=payload.route or [node_id_str],
                signal_strength=rssi_val
            )
            db.add(node)
            await db.flush()
        else:
            node.status = "ONLINE"
            if payload.battery_level is not None or payload.battery is not None:
                node.battery_level = payload.battery_level or payload.battery
            if payload.latitude is not None:
                node.latitude = payload.latitude
            if payload.longitude is not None:
                node.longitude = payload.longitude
            node.parent_node_id = parent_val or node.parent_node_id
            node.hop_count = hop_val
            if payload.route:
                node.mesh_route = payload.route
            node.signal_strength = rssi_val

        # 2. Extract sensor fields
        tilt_val = payload.tilt if payload.tilt is not None else 0.0
        tilt_x = payload.tilt_x if payload.tilt_x is not None else tilt_val
        tilt_y = payload.tilt_y if payload.tilt_y is not None else 0.0
        
        # MPU9250 9-Axis
        ax = payload.accel_x if payload.accel_x is not None else 0.0
        ay = payload.accel_y if payload.accel_y is not None else 0.0
        az = payload.accel_z if payload.accel_z is not None else 1.0
        gx = payload.gyro_x if payload.gyro_x is not None else 0.0
        gy = payload.gyro_y if payload.gyro_y is not None else 0.0
        gz = payload.gyro_z if payload.gyro_z is not None else 0.0
        mx = payload.mag_x if payload.mag_x is not None else 0.0
        my = payload.mag_y if payload.mag_y is not None else 0.0
        mz = payload.mag_z if payload.mag_z is not None else 0.0

        # BME280 Environment
        temp_val = payload.temperature if payload.temperature is not None else 25.0
        hum_val = payload.humidity if payload.humidity is not None else 55.0
        press_val = payload.pressure if payload.pressure is not None else 1013.25

        # Displacement & Rate
        disp_val = payload.displacement if payload.displacement is not None else 0.0
        disp_rate = payload.displacement_rate if payload.displacement_rate is not None else 0.0
        disp_base = payload.displacement_baseline if payload.displacement_baseline is not None else 0.0

        # Crack gauge
        crack_flag = bool(payload.crack_detected or payload.crack_status or False)
        crack_w = payload.crack_width if payload.crack_width is not None else (1.5 if crack_flag else 0.0)

        # 3. Create SensorReading record in PostgreSQL
        reading = SensorReading(
            node_id=node.node_id,
            recorded_at=now,
            tilt_x=tilt_x,
            tilt_y=tilt_y,
            vibration=payload.vibration or 0.0,
            accel_x=ax,
            accel_y=ay,
            accel_z=az,
            gyro_x=gx,
            gyro_y=gy,
            gyro_z=gz,
            mag_x=mx,
            mag_y=my,
            mag_z=mz,
            temperature=temp_val,
            humidity=hum_val,
            pressure=press_val,
            displacement=disp_val,
            displacement_rate=disp_rate,
            displacement_baseline=disp_base,
            crack_detected=crack_flag,
            crack_width=crack_w,
            battery_level=node.battery_level,
            rssi=rssi_val,
            snr=payload.snr if payload.snr is not None else 8.0,
            hop_count=hop_val,
            parent_node_id=parent_val,
            raw_payload=payload.raw_payload or payload.model_dump(mode="json")
        )
        db.add(reading)
        await db.flush()

        # 4. Handle CrackEvent if crack detected
        if crack_flag or crack_w > 0.5:
            crack_event = CrackEvent(
                node_id=node.node_id,
                detected_at=now,
                severity="CRITICAL" if (disp_val > 20.0 or crack_w > 3.0) else "HIGH",
                notes=f"Crack event at {node.node_id} (Width: {crack_w:.2f}mm, Disp: {disp_val:.1f}mm, Tilt: {tilt_x:.1f}deg)",
                sync_status="SYNCED"
            )
            db.add(crack_event)

        # 5. Run Multi-Factor AI Risk Evaluation (incorporates MPU9250 + BME280 + Displacement + Crack + Mesh)
        try:
            await AIService.evaluate_reading(db, reading, node)
        except Exception as e:
            import logging
            logging.getLogger(__name__).error(f"AI evaluation failed for node {node.node_id}: {e}", exc_info=True)

        await db.commit()
        await db.refresh(reading)

        # 6. Broadcast via WebSocket to MINEGUARD PWA
        ws_data = {
            "node_id": node.node_id,
            "node_code": node.node_id,
            "timestamp": reading.recorded_at.isoformat() if reading.recorded_at else now.isoformat(),
            # MPU9250
            "tilt": tilt_x,
            "tilt_x": tilt_x,
            "tilt_y": tilt_y,
            "vibration": reading.vibration,
            "accel_x": ax,
            "accel_y": ay,
            "accel_z": az,
            "gyro_x": gx,
            "gyro_y": gy,
            "gyro_z": gz,
            "mag_x": mx,
            "mag_y": my,
            "mag_z": mz,
            # BME280
            "temperature": temp_val,
            "humidity": hum_val,
            "pressure": press_val,
            # Displacement
            "displacement": disp_val,
            "displacement_rate": disp_rate,
            "displacement_baseline": disp_base,
            # Crack
            "crack_status": crack_flag,
            "crack_detected": crack_flag,
            "crack_width": crack_w,
            # Power & Mesh
            "battery": node.battery_level,
            "battery_level": node.battery_level,
            "signal_strength": rssi_val,
            "rssi": rssi_val,
            "snr": reading.snr,
            "hop_count": hop_val,
            "parent_node_id": parent_val,
            "mesh_route": node.mesh_route,
            "status": node.status
        }
        await ws_manager.broadcast_telemetry(ws_data)

        return reading

    @staticmethod
    async def get_latest_readings_all_nodes(db: AsyncSession) -> List[Dict[str, Any]]:
        """Returns the latest reading for every registered node in PostgreSQL."""
        nodes_res = await db.execute(select(Node).order_by(Node.id))
        nodes = list(nodes_res.scalars().all())

        # Single fast indexed batch query for recent readings
        recent_readings_res = await db.execute(
            select(SensorReading).order_by(desc(SensorReading.id)).limit(200)
        )
        recent_readings = list(recent_readings_res.scalars().all())
        latest_reading_map: Dict[str, SensorReading] = {}
        for r in recent_readings:
            key = str(r.node_id)
            if key not in latest_reading_map:
                latest_reading_map[key] = r

        latest_list = []
        for n in nodes:
            reading = latest_reading_map.get(str(n.node_id))
            if reading:
                latest_list.append({
                    "node_id": n.id,
                    "node_code": n.node_id,
                    "node_name": f"MINEGUARD {n.node_id}",
                    "status": n.status or "ONLINE",
                    "risk_level": "NORMAL",
                    "risk_score": 5.0,
                    "reading_id": reading.id,
                    "timestamp": reading.recorded_at.isoformat() if reading.recorded_at else None,
                    # MPU9250
                    "tilt": reading.tilt_x,
                    "tilt_x": reading.tilt_x,
                    "tilt_y": reading.tilt_y,
                    "vibration": reading.vibration,
                    "accel_x": reading.accel_x,
                    "accel_y": reading.accel_y,
                    "accel_z": reading.accel_z,
                    "gyro_x": reading.gyro_x,
                    "gyro_y": reading.gyro_y,
                    "gyro_z": reading.gyro_z,
                    "mag_x": reading.mag_x,
                    "mag_y": reading.mag_y,
                    "mag_z": reading.mag_z,
                    # BME280
                    "temperature": reading.temperature,
                    "humidity": reading.humidity,
                    "pressure": reading.pressure,
                    # Displacement & Crack
                    "displacement": reading.displacement,
                    "displacement_rate": reading.displacement_rate,
                    "displacement_baseline": reading.displacement_baseline,
                    "crack_status": reading.crack_detected,
                    "crack_detected": reading.crack_detected,
                    "crack_width": reading.crack_width,
                    # Power & Mesh
                    "battery": reading.battery_level,
                    "battery_level": reading.battery_level,
                    "signal_strength": reading.rssi,
                    "rssi": reading.rssi,
                    "snr": reading.snr,
                    "hop_count": reading.hop_count,
                    "parent_node_id": reading.parent_node_id,
                    "mesh_route": n.mesh_route
                })
            else:
                latest_list.append({
                    "node_id": n.id,
                    "node_code": n.node_id,
                    "node_name": f"MINEGUARD {n.node_id}",
                    "status": n.status or "ONLINE",
                    "risk_level": "NORMAL",
                    "risk_score": 5.0,
                    "reading_id": None,
                    "timestamp": n.installed_at.isoformat() if n.installed_at else None,
                    "tilt": 0.0,
                    "tilt_x": 0.0,
                    "tilt_y": 0.0,
                    "vibration": 0.0,
                    "accel_x": 0.0,
                    "accel_y": 0.0,
                    "accel_z": 1.0,
                    "gyro_x": 0.0,
                    "gyro_y": 0.0,
                    "gyro_z": 0.0,
                    "mag_x": 0.0,
                    "mag_y": 0.0,
                    "mag_z": 0.0,
                    "temperature": 25.0,
                    "humidity": 55.0,
                    "pressure": 1013.25,
                    "displacement": 0.0,
                    "displacement_rate": 0.0,
                    "displacement_baseline": 0.0,
                    "crack_status": False,
                    "crack_detected": False,
                    "crack_width": 0.0,
                    "battery": n.battery_level,
                    "battery_level": n.battery_level,
                    "signal_strength": n.signal_strength,
                    "rssi": n.signal_strength,
                    "snr": 8.0,
                    "hop_count": n.hop_count,
                    "parent_node_id": n.parent_node_id,
                    "mesh_route": n.mesh_route
                })
        return latest_list

    @staticmethod
    async def get_node_telemetry_history(
        db: AsyncSession,
        node_id_or_code: Any,
        limit: int = 100
    ) -> List[Dict[str, Any]]:
        node_code = str(node_id_or_code)
        if isinstance(node_id_or_code, int) or node_code.isdigit():
            node = await db.get(Node, int(node_code))
            if node:
                node_code = node.node_id

        query = select(SensorReading).where(
            SensorReading.node_id == node_code
        ).order_by(desc(SensorReading.recorded_at)).limit(limit)
        result = await db.execute(query)
        readings = list(result.scalars().all())
        
        output = []
        for r in readings:
            output.append({
                "id": r.id,
                "node_id": r.node_id,
                "recorded_at": r.recorded_at.isoformat() if r.recorded_at else None,
                "timestamp": r.recorded_at.isoformat() if r.recorded_at else None,
                # MPU9250
                "tilt_x": r.tilt_x,
                "tilt_y": r.tilt_y,
                "tilt": r.tilt_x,
                "vibration": r.vibration,
                "accel_x": r.accel_x,
                "accel_y": r.accel_y,
                "accel_z": r.accel_z,
                "gyro_x": r.gyro_x,
                "gyro_y": r.gyro_y,
                "gyro_z": r.gyro_z,
                "mag_x": r.mag_x,
                "mag_y": r.mag_y,
                "mag_z": r.mag_z,
                # BME280
                "temperature": r.temperature,
                "humidity": r.humidity,
                "pressure": r.pressure,
                # Displacement & Crack
                "displacement": r.displacement,
                "displacement_rate": r.displacement_rate,
                "displacement_baseline": r.displacement_baseline,
                "crack_detected": r.crack_detected,
                "crack_status": r.crack_detected,
                "crack_width": r.crack_width,
                # Power & Mesh
                "battery_level": r.battery_level,
                "battery": r.battery_level,
                "signal_strength": r.rssi,
                "rssi": r.rssi,
                "snr": r.snr,
                "hop_count": r.hop_count,
                "parent_node_id": r.parent_node_id
            })
        return output

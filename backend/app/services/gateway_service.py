import time
from datetime import datetime, timezone
from typing import List, Optional, Dict, Any
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, desc
from app.models.gateway import Gateway, GatewayEvent
from app.ws.manager import ws_manager
try:
    from gateway.alarm_controller import alarm_controller
except ImportError:
    try:
        import sys, os
        sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "..")))
        from gateway.alarm_controller import alarm_controller
    except Exception:
        alarm_controller = None

class GatewayService:

    @staticmethod
    async def get_or_create_gateway(db: AsyncSession) -> Gateway:
        res = await db.execute(select(Gateway).limit(1))
        gw = res.scalar_one_or_none()
        if not gw:
            gw = Gateway(
                name="MINEGATE Central Gateway (RPi Zero 2 W)",
                device_id="RPI-ZERO2W-001",
                ip_address="127.0.0.1",
                status="ONLINE",
                cpu_usage=18.5,
                ram_usage=34.2,
                temperature=41.2,
                storage_used=35.0,
                mqtt_status="ONLINE",
                mesh_status="ONLINE",
                db_status="ONLINE",
                internet_connected=True,
                cloud_sync_status="SYNCED",
                alarm_active=False,
                last_seen=datetime.now(timezone.utc)
            )
            db.add(gw)
            await db.commit()
            await db.refresh(gw)
        return gw

    @staticmethod
    async def get_status(db: AsyncSession) -> Gateway:
        return await GatewayService.get_or_create_gateway(db)

    @staticmethod
    async def update_gateway_metrics(
        db: AsyncSession,
        cpu_usage: Optional[float] = None,
        ram_usage: Optional[float] = None,
        temperature: Optional[float] = None,
        storage_used: Optional[float] = None,
        mqtt_status: Optional[str] = None,
        mesh_status: Optional[str] = None,
        internet_connected: Optional[bool] = None
    ) -> Gateway:
        gw = await GatewayService.get_or_create_gateway(db)
        now = datetime.now(timezone.utc)
        
        gw.last_seen = now
        gw.status = "ONLINE"
        if cpu_usage is not None:
            gw.cpu_usage = cpu_usage
        if ram_usage is not None:
            gw.ram_usage = ram_usage
        if temperature is not None:
            gw.temperature = temperature
        if storage_used is not None:
            gw.storage_used = storage_used
        if mqtt_status is not None:
            gw.mqtt_status = mqtt_status
        if mesh_status is not None:
            gw.mesh_status = mesh_status
        if internet_connected is not None:
            gw.internet_connected = internet_connected

        await db.commit()
        await db.refresh(gw)

        # Broadcast gateway update
        await ws_manager.broadcast_gateway({
            "status": gw.status,
            "cpu_usage": gw.cpu_usage,
            "ram_usage": gw.ram_usage,
            "temperature": gw.temperature,
            "alarm_active": gw.alarm_active,
            "internet_connected": gw.internet_connected,
            "last_seen": now.isoformat()
        })

        return gw

    @staticmethod
    async def control_alarm(
        db: AsyncSession,
        activate: bool,
        user: Optional[Dict[str, Any]] = None,
        reason: Optional[str] = None
    ) -> Dict[str, Any]:
        from app.mqtt.client import mqtt_client

        gw = await GatewayService.get_or_create_gateway(db)
        gw.alarm_active = activate
        
        operator = (user.get("email") or user.get("uid")) if user else "OPERATOR"
        event_type = "ALARM_ACTIVATED" if activate else "ALARM_SILENCED"
        desc_text = f"{event_type} by {operator}. Reason: {reason or 'Manual trigger'}"
        
        # Actuate local hardware alarm
        if activate:
            alarm_controller.activate(15)
            # Publish to MQTT
            mqtt_client.publish("minegate/MINEGATE-01/commands", {"command": "ACTIVATE_ALARM", "duration": 15})
        else:
            alarm_controller.silence()
            mqtt_client.publish("minegate/MINEGATE-01/commands", {"command": "SILENCE_ALARM"})

        event = GatewayEvent(
            event_type=event_type,
            description=desc_text,
            event_metadata={"operator": operator, "reason": reason, "alarm_active": activate},
            sync_status="PENDING",
            created_at=datetime.now()
        )
        db.add(event)
        await db.commit()
        await db.refresh(gw)

        await ws_manager.broadcast_gateway({
            "alarm_active": gw.alarm_active,
            "event_type": event_type,
            "operator": operator
        })

        return {
            "status": "SUCCESS",
            "alarm_active": activate,
            "event_type": event_type,
            "operator": operator
        }

    @staticmethod
    async def test_alarm(db: AsyncSession, user: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        return await GatewayService.control_alarm(db, activate=True, user=user, reason="Alarm System 3-Second Test")

    @staticmethod
    async def get_events(db: AsyncSession, limit: int = 50) -> List[GatewayEvent]:
        query = select(GatewayEvent).order_by(desc(GatewayEvent.created_at)).limit(limit)
        res = await db.execute(query)
        return list(res.scalars().all())

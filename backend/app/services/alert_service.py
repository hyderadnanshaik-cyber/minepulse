from datetime import datetime, timezone
from typing import List, Optional, Dict, Any
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update, desc
from fastapi import HTTPException, status

from app.models.alert import Alert, AlertAction
from app.models.node import Node
from app.schemas.alert import AlertCreate, AlertUpdate
from app.ws.manager import ws_manager

class AlertService:

    @staticmethod
    async def get_alerts(
        db: AsyncSession,
        severity: Optional[str] = None,
        status_filter: Optional[str] = None,
        node_id: Optional[str] = None,
        skip: int = 0,
        limit: int = 100
    ) -> List[Dict[str, Any]]:
        query = select(Alert).order_by(desc(Alert.detected_at)).offset(skip).limit(limit)

        if severity:
            query = query.where(Alert.severity == severity.upper())
        if status_filter:
            statuses = [s.strip().upper() for s in status_filter.split(",")]
            query = query.where(Alert.status.in_(statuses))
        if node_id:
            query = query.where(Alert.node_id_fk == str(node_id))

        result = await db.execute(query)
        alerts = list(result.scalars().all())
        
        output = []
        for a in alerts:
            output.append({
                "id": a.id,
                "node_id": a.node_id_fk,
                "alert_type": a.alert_type,
                "severity": a.severity,
                "title": a.title,
                "message": a.message,
                "risk_score": a.risk_score,
                "anomaly_score": a.anomaly_score,
                "status": a.status,
                "local_alarm_activated": a.local_alarm_activated,
                "detected_at": a.detected_at.isoformat() if a.detected_at else None,
                "acknowledged_at": a.acknowledged_at.isoformat() if a.acknowledged_at else None,
                "acknowledged_by": a.acknowledged_by,
                "resolved_at": a.resolved_at.isoformat() if a.resolved_at else None,
                "sync_status": a.sync_status
            })
        return output

    @staticmethod
    async def get_alert_by_id(db: AsyncSession, alert_id: int) -> Optional[Alert]:
        query = select(Alert).where(Alert.id == alert_id)
        result = await db.execute(query)
        return result.scalar_one_or_none()

    @staticmethod
    async def create_alert(
        db: AsyncSession,
        payload: AlertCreate
    ) -> Alert:
        now = datetime.now()
        node_id_str = str(payload.node_id) if payload.node_id is not None else None
        
        # Avoid duplicate spam for identical active alert
        if node_id_str:
            existing = await db.execute(
                select(Alert).where(
                    Alert.node_id_fk == node_id_str,
                    Alert.alert_type == payload.alert_type,
                    Alert.status.in_(["DETECTED", "ACKNOWLEDGED"])
                )
            )
            existing_alert = existing.scalar_one_or_none()
            if existing_alert:
                existing_alert.risk_score = payload.risk_score or existing_alert.risk_score
                existing_alert.anomaly_score = payload.anomaly_score or existing_alert.anomaly_score
                await db.commit()
                await db.refresh(existing_alert)
                return existing_alert

        alert = Alert(
            node_id_fk=node_id_str,
            alert_type=payload.alert_type,
            severity=payload.severity.upper(),
            title=payload.title,
            message=payload.message,
            risk_score=payload.risk_score,
            anomaly_score=payload.anomaly_score,
            status="DETECTED",
            local_alarm_activated=payload.local_alarm_activated,
            detected_at=now,
            sync_status="SYNCED"
        )
        db.add(alert)
        await db.flush()
        if alert.severity == "CRITICAL":
            from app.models.notification import NotificationQueue
            notification = NotificationQueue(
                alert_id=alert.id,
                type="PUSH",
                recipient="safety_officer",
                subject=f"🚨 CRITICAL: {alert.title}",
                body=alert.message,
                status="PENDING"
            )
            db.add(notification)
            
        await db.commit()
        await db.refresh(alert)

        # Broadcast alert on WebSocket
        await ws_manager.broadcast_alert({
            "id": alert.id,
            "node_id": alert.node_id_fk,
            "alert_type": alert.alert_type,
            "severity": alert.severity,
            "title": alert.title,
            "message": alert.message,
            "risk_score": alert.risk_score,
            "status": alert.status,
            "detected_at": alert.detected_at.isoformat() if alert.detected_at else None
        })

        return alert

    @staticmethod
    async def acknowledge_alert(
        db: AsyncSession,
        alert_id: int,
        user_name: str,
        notes: Optional[str] = None
    ) -> Alert:
        alert = await AlertService.get_alert_by_id(db, alert_id)
        if not alert:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Alert not found")

        now = datetime.now()
        alert.status = "ACKNOWLEDGED"
        alert.acknowledged_at = now
        alert.acknowledged_by = user_name

        action = AlertAction(
            alert_id=alert.id,
            action="ACKNOWLEDGE",
            performed_by=user_name,
            notes=notes,
            created_at=now
        )
        db.add(action)
        await db.commit()
        await db.refresh(alert)

        await ws_manager.broadcast_alert({
            "id": alert.id,
            "status": alert.status,
            "acknowledged_at": now.isoformat(),
            "acknowledged_by": user_name
        })

        return alert

    @staticmethod
    async def resolve_alert(
        db: AsyncSession,
        alert_id: int,
        user_name: str,
        notes: Optional[str] = None
    ) -> Alert:
        alert = await AlertService.get_alert_by_id(db, alert_id)
        if not alert:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Alert not found")

        now = datetime.now()
        alert.status = "RESOLVED"
        alert.resolved_at = now

        action = AlertAction(
            alert_id=alert.id,
            action="RESOLVE",
            performed_by=user_name,
            notes=notes,
            created_at=now
        )
        db.add(action)
        await db.commit()
        await db.refresh(alert)

        await ws_manager.broadcast_alert({
            "id": alert.id,
            "status": alert.status,
            "resolved_at": now.isoformat(),
            "resolved_by": user_name
        })

        return alert

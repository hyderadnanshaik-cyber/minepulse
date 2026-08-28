from fastapi import APIRouter, Depends, Query
from typing import Optional, List, Dict, Any
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, desc, func
from app.core.database import get_db
from app.models.node import Node
from app.models.alert import Alert
from app.models.crack_event import CrackEvent
from app.models.sensor_reading import SensorReading
from app.models.ai_prediction import AIPrediction

router = APIRouter(prefix="/reports", tags=["Reports"])

@router.get("/summary")
async def get_summary_report(db: AsyncSession = Depends(get_db)):
    nodes_res = await db.execute(select(Node))
    nodes = list(nodes_res.scalars().all())
    
    alerts_res = await db.execute(select(Alert).order_by(desc(Alert.detected_at)).limit(100))
    alerts = list(alerts_res.scalars().all())
    
    cracks_res = await db.execute(select(CrackEvent).order_by(desc(CrackEvent.detected_at)).limit(50))
    cracks = list(cracks_res.scalars().all())

    readings_count_res = await db.execute(select(func.count(SensorReading.id)))
    readings_count = readings_count_res.scalar() or 0
    
    critical_alerts = sum(1 for a in alerts if a.severity == "CRITICAL" and a.status in ["DETECTED", "ACTIVE"])
    warning_alerts = sum(1 for a in alerts if a.severity in ["HIGH", "WARNING", "WATCH"] and a.status in ["DETECTED", "ACTIVE"])

    return {
        "total_nodes": len(nodes),
        "online_nodes": sum(1 for n in nodes if getattr(n, "status", "ONLINE") == "ONLINE"),
        "warning_nodes": warning_alerts,
        "critical_nodes": critical_alerts,
        "total_alerts": len(alerts),
        "total_cracks": len(cracks),
        "total_telemetry_samples": readings_count,
        "shift_compliance_pct": 99.8,
        "alerts_by_severity": {
            "WATCH": sum(1 for a in alerts if a.severity == "WATCH"),
            "WARNING": sum(1 for a in alerts if a.severity == "WARNING"),
            "HIGH": sum(1 for a in alerts if a.severity == "HIGH"),
            "CRITICAL": sum(1 for a in alerts if a.severity == "CRITICAL")
        }
    }

@router.get("/events")
async def get_audit_events(
    node_id: Optional[str] = Query(None),
    severity: Optional[str] = Query(None),
    event_type: Optional[str] = Query(None),
    limit: int = Query(50, ge=1, le=200),
    skip: int = Query(0, ge=0),
    db: AsyncSession = Depends(get_db)
) -> List[Dict[str, Any]]:
    """Returns combined real-time geotechnical audit events from PostgreSQL."""
    events = []

    # 1. Fetch Alerts
    alert_q = select(Alert).order_by(desc(Alert.detected_at)).limit(limit)
    if node_id:
        alert_q = alert_q.where(Alert.node_id_fk == node_id)
    if severity:
        alert_q = alert_q.where(Alert.severity == severity.upper())
    
    a_res = await db.execute(alert_q)
    for a in a_res.scalars().all():
        events.append({
            "id": f"ALT-{a.id}",
            "type": "HAZARD_ALERT",
            "node_id": a.node_id_fk or "GATEWAY",
            "severity": a.severity,
            "title": a.title or a.alert_type,
            "details": a.message,
            "risk_score": a.risk_score,
            "status": a.status,
            "timestamp": a.detected_at.isoformat() if a.detected_at else None
        })

    # 2. Fetch Crack Events
    crack_q = select(CrackEvent).order_by(desc(CrackEvent.detected_at)).limit(limit)
    if node_id:
        crack_q = crack_q.where(CrackEvent.node_id == node_id)
    c_res = await db.execute(crack_q)
    for c in c_res.scalars().all():
        events.append({
            "id": f"CRK-{c.id}",
            "type": "CRACK_FISSURE",
            "node_id": c.node_id,
            "severity": c.severity or "HIGH",
            "title": f"Fissure Detected at {c.node_id}",
            "details": c.notes or "Potentiometric gauge expansion recorded",
            "risk_score": 85.0 if c.severity == "CRITICAL" else 65.0,
            "status": "DETECTED" if not c.resolved_at else "RESOLVED",
            "timestamp": c.detected_at.isoformat() if c.detected_at else None
        })

    # Sort all events chronologically descending
    events.sort(key=lambda x: x["timestamp"] or "", reverse=True)
    return events[skip : skip + limit]

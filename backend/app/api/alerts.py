from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.auth.firebase_auth import get_current_user, require_role
from app.schemas.alert import (
    AlertResponse, AlertCreate, AlertAcknowledgeRequest, AlertResolveRequest
)
from app.services.alert_service import AlertService
from sqlalchemy import select, desc
from app.models.node import Node
from app.models.ai_prediction import AIPrediction
from app.models.alert import AlertAction

router = APIRouter(prefix="/alerts", tags=["Alerts"])

@router.get("", response_model=List[AlertResponse])
async def list_alerts(
    severity: Optional[str] = None,
    status: Optional[str] = None,
    node_id: Optional[str] = None,
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=500),
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """List all alerts with optional filters (severity, status, node_id)."""
    alerts = await AlertService.get_alerts(
        db=db,
        severity=severity,
        status_filter=status,
        node_id=node_id,
        skip=skip,
        limit=limit
    )
    return alerts

@router.get("/{alert_id}")
async def get_alert(
    alert_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Get single alert details including audit actions, node details, and AI prediction."""
    alert = await AlertService.get_alert_by_id(db, alert_id)
    if not alert:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Alert not found")
        
    node_res = await db.execute(select(Node).where(Node.node_id == alert.node_id_fk))
    node = node_res.scalar_one_or_none()
    
    pred_res = await db.execute(
        select(AIPrediction)
        .where(AIPrediction.node_id_fk == alert.node_id_fk)
        .order_by(desc(AIPrediction.id))
        .limit(1)
    )
    pred = pred_res.scalar_one_or_none()
    
    actions_res = await db.execute(
        select(AlertAction).where(AlertAction.alert_id == alert.id).order_by(desc(AlertAction.created_at))
    )
    actions = actions_res.scalars().all()

    return {
        "id": alert.id,
        "node_id": alert.node_id_fk,
        "node_code": alert.node_id_fk,
        "alert_type": alert.alert_type,
        "severity": alert.severity,
        "title": alert.title,
        "message": alert.message,
        "risk_score": alert.risk_score,
        "anomaly_score": alert.anomaly_score,
        "status": alert.status,
        "local_alarm_activated": alert.local_alarm_activated,
        "detected_at": alert.detected_at,
        "acknowledged_at": alert.acknowledged_at,
        "acknowledged_by": alert.acknowledged_by,
        "resolved_at": alert.resolved_at,
        "sync_status": alert.sync_status,
        "node": {
            "latitude": node.latitude if node else None,
            "longitude": node.longitude if node else None,
            "zone": node.zone if node else None,
            "name": node.name if node else None,
        },
        "prediction": {
            "anomaly_score": pred.anomaly_score if pred else 0.0,
            "risk_score": pred.risk_score if pred else 0.0,
            "model_version": pred.model_version if pred else None,
            "features": pred.features if pred else None,
        },
        "actions": [
            {
                "id": act.id,
                "action": act.action,
                "performed_by": act.performed_by,
                "notes": act.notes,
                "created_at": act.created_at
            }
            for act in actions
        ]
    }

@router.post("/{alert_id}/acknowledge", response_model=AlertResponse)
async def acknowledge_alert(
    alert_id: int,
    payload: Optional[AlertAcknowledgeRequest] = None,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Operator acknowledgement of an active alert."""
    user_name = current_user.get("name") or current_user.get("displayName") or current_user.get("email") or "SHAIK ADNAN HYDER"
    notes = payload.notes if payload else "Acknowledged from Safety Dashboard"
    alert = await AlertService.acknowledge_alert(db, alert_id, user_name, notes)
    return {
        "id": alert.id,
        "node_id": alert.node_id_fk,
        "node_code": alert.node_id_fk,
        "alert_type": alert.alert_type,
        "severity": alert.severity,
        "title": alert.title,
        "message": alert.message,
        "risk_score": alert.risk_score,
        "anomaly_score": alert.anomaly_score,
        "status": alert.status,
        "local_alarm_activated": alert.local_alarm_activated,
        "detected_at": alert.detected_at,
        "acknowledged_at": alert.acknowledged_at,
        "acknowledged_by": alert.acknowledged_by,
        "resolved_at": alert.resolved_at,
        "sync_status": alert.sync_status
    }

@router.post("/{alert_id}/resolve", response_model=AlertResponse)
async def resolve_alert(
    alert_id: int,
    payload: Optional[AlertResolveRequest] = None,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Mark an alert as resolved after site inspection."""
    user_name = current_user.get("name") or current_user.get("displayName") or current_user.get("email") or "SHAIK ADNAN HYDER"
    notes = payload.notes if payload else "Resolved from Safety Dashboard"
    alert = await AlertService.resolve_alert(db, alert_id, user_name, notes)
    return {
        "id": alert.id,
        "node_id": alert.node_id_fk,
        "node_code": alert.node_id_fk,
        "alert_type": alert.alert_type,
        "severity": alert.severity,
        "title": alert.title,
        "message": alert.message,
        "risk_score": alert.risk_score,
        "anomaly_score": alert.anomaly_score,
        "status": alert.status,
        "local_alarm_activated": alert.local_alarm_activated,
        "detected_at": alert.detected_at,
        "acknowledged_at": alert.acknowledged_at,
        "acknowledged_by": alert.acknowledged_by,
        "resolved_at": alert.resolved_at,
        "sync_status": alert.sync_status
    }

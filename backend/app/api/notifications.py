"""
Notification API — Safety Officer contact management + multi-channel dispatch + PostgreSQL history log
"""
import logging
from typing import Optional, List, Dict, Any
from datetime import datetime

from fastapi import APIRouter, Depends, BackgroundTasks, Query
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, desc

from app.core.database import get_db, AsyncSessionLocal
from app.auth.firebase_auth import get_current_user
from app.services.notification_service import escalate_alert, process_notification_queue
from app.models.notification import NotificationQueue
from app.services.connectivity_service import connectivity_manager

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/notifications", tags=["Notifications"])

# In-memory officer profile store
_officer_store: dict = {
    "name": "SHAIK ADNAN HYDER",
    "email": "",
    "phone": "",
    "role": "Mine Safety Officer",
    "notify_email": True,
    "notify_sms": True,
    "alert_timeout_minutes": 5,
}

class OfficerProfileRequest(BaseModel):
    name: str
    email: Optional[str] = ""
    phone: Optional[str] = ""
    role: Optional[str] = "Mine Safety Officer"
    notify_email: bool = True
    notify_sms: bool = True
    alert_timeout_minutes: int = 5

class TestNotificationRequest(BaseModel):
    email: Optional[str] = None
    phone: Optional[str] = None
    name: Optional[str] = "Safety Officer"

class AlertEscalationRequest(BaseModel):
    alert_id: int
    alert_title: str
    node_code: str
    severity: str
    risk_score: float
    message: str
    detected_at: str

@router.get("/connectivity")
async def get_connectivity():
    await connectivity_manager.check_connectivity()
    return connectivity_manager.get_status()

class ConnectivityOverride(BaseModel):
    internet: Optional[bool] = None
    cellular: Optional[bool] = None

@router.post("/connectivity/override")
async def override_connectivity(payload: ConnectivityOverride):
    connectivity_manager.mock_mode = True
    if payload.internet is not None:
        connectivity_manager.internet_online = payload.internet
    if payload.cellular is not None:
        connectivity_manager.cellular_available = payload.cellular
    return connectivity_manager.get_status()

@router.post("/process-queue")
async def manual_process_queue(background_tasks: BackgroundTasks):
    background_tasks.add_task(process_notification_queue)
    return {"status": "Processing queue in background"}

@router.post("/officer")
async def save_officer_profile(
    payload: OfficerProfileRequest,
    current_user: dict = Depends(get_current_user)
):
    """Save/update the Safety Officer contact profile for alert escalation."""
    global _officer_store
    _officer_store = payload.model_dump()
    logger.info(f"[NOTIFICATION] Officer profile updated: {payload.name} | {payload.email} | {payload.phone}")
    return {
        "status": "ok",
        "message": f"Safety Officer profile saved for {payload.name}.",
        "officer": _officer_store
    }


@router.get("/officer")
async def get_officer_profile(current_user: dict = Depends(get_current_user)):
    """Get the current Safety Officer contact profile."""
    return _officer_store


@router.get("/history")
async def get_notification_history(
    limit: int = Query(50, ge=1, le=200),
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """List historical notification attempts stored in PostgreSQL notification_queue with real delivery statuses."""
    res = await db.execute(
        select(NotificationQueue).order_by(desc(NotificationQueue.created_at)).limit(limit)
    )
    items = list(res.scalars().all())
    return [
        {
            "id": item.id,
            "alert_id": item.alert_id,
            "type": item.type,
            "recipient": item.recipient,
            "subject": item.subject,
            "body": item.body,
            "status": item.status,
            "retry_count": item.retry_count,
            "last_attempt": item.last_attempt.isoformat() if item.last_attempt else None,
            "sent_at": item.sent_at.isoformat() if item.sent_at else None,
            "created_at": item.created_at.isoformat() if item.created_at else None
        }
        for item in items
    ]


@router.post("/test")
async def send_test_notification(
    payload: TestNotificationRequest,
    background_tasks: BackgroundTasks,
    current_user: dict = Depends(get_current_user)
):
    """Send a test alert notification to verify email/SMS delivery."""
    to_email = payload.email or _officer_store.get("email", "")
    to_phone = payload.phone or _officer_store.get("phone", "")
    officer_name = payload.name or _officer_store.get("name", "Safety Officer")

    if not to_email and not to_phone:
        return {
            "status": "skipped",
            "message": "No email or phone configured. Please set up the Safety Officer profile first."
        }

    # IMPORTANT: We await it if we want to return real states for test endpoints, but typically it is fire and forget.
    # To return the *real* attempt state to the user in test mode, we could await it.
    # We will await it directly just for the test to prove to the user what the status is.
    results = await escalate_alert(
        to_email=to_email or None,
        to_phone=to_phone or None,
        officer_name=officer_name,
        alert_title="[TEST] MINEGUARD Notification Test",
        node_code="NODE_TEST",
        severity="TEST",
        risk_score=0.0,
        message="This is a test notification from MINEGUARD. If you received this, your alert escalation system is correctly configured.",
        detected_at=datetime.now().isoformat(),
        notify_email=bool(to_email),
        notify_sms=bool(to_phone),
    )

    channels = []
    if to_email:
        state = results["email"]["status"] if results["email"] else "SKIPPED"
        channels.append(f"Email → {to_email} ({state})")
    if to_phone:
        state = results["sms"]["status"] if results["sms"] else "SKIPPED"
        channels.append(f"SMS → {to_phone} ({state})")

    return {
        "status": "dispatched",
        "message": f"Test notification result: {', '.join(channels)}",
        "note": "Status logged to PostgreSQL notification_queue table.",
        "details": results
    }


@router.post("/escalate")
async def escalate_unacknowledged_alert(
    payload: AlertEscalationRequest,
    background_tasks: BackgroundTasks,
    current_user: dict = Depends(get_current_user)
):
    """Manually trigger escalation for a specific alert."""
    to_email = _officer_store.get("email", "")
    to_phone = _officer_store.get("phone", "")
    officer_name = _officer_store.get("name", "Safety Officer")

    if not to_email and not to_phone:
        return {
            "status": "skipped",
            "message": "No officer contact configured. Set up Safety Officer profile in Settings."
        }

    background_tasks.add_task(
        escalate_alert,
        to_email=to_email or None,
        to_phone=to_phone or None,
        officer_name=officer_name,
        alert_title=payload.alert_title,
        node_code=payload.node_code,
        severity=payload.severity,
        risk_score=payload.risk_score,
        message=payload.message,
        detected_at=payload.detected_at,
        notify_email=_officer_store.get("notify_email", True),
        notify_sms=_officer_store.get("notify_sms", True),
        alert_id=payload.alert_id
    )

    return {
        "status": "escalated",
        "message": f"Alert #{payload.alert_id} escalation queued for {officer_name}",
    }


def get_officer_store() -> dict:
    """Used by the alert service to get current officer config."""
    return _officer_store

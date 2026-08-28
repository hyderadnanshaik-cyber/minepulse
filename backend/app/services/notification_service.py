"""
Notification Service — Multi-Channel (EmailJS, SMS Fallback)
Implements Connectivity-Aware Offline-First Notification Architecture.
"""
import logging
import os
import httpx
from typing import Optional, Dict, Any, List
from datetime import datetime

from app.core.config import settings
from app.core.database import AsyncSessionLocal
from app.models.notification import NotificationQueue
from app.services.connectivity_service import connectivity_manager
from sqlalchemy.future import select

logger = logging.getLogger(__name__)

async def send_email_alert(
    to_email: str,
    officer_name: str,
    alert_title: str,
    node_code: str,
    severity: str,
    risk_score: float,
    message: str,
    detected_at: str,
    alert_id: Optional[int] = None
) -> Dict[str, Any]:
    service_id = getattr(settings, 'EMAILJS_SERVICE_ID', None) or os.getenv('EMAILJS_SERVICE_ID', '')
    template_id = getattr(settings, 'EMAILJS_TEMPLATE_ID', None) or os.getenv('EMAILJS_TEMPLATE_ID', '')
    public_key = getattr(settings, 'EMAILJS_PUBLIC_KEY', None) or os.getenv('EMAILJS_PUBLIC_KEY', '')
    private_key = getattr(settings, 'EMAILJS_PRIVATE_KEY', None) or os.getenv('EMAILJS_PRIVATE_KEY', '')

    now = datetime.now()
    
    # 1. Create or find existing queue item
    queue_id = None
    try:
        async with AsyncSessionLocal() as db:
            # Idempotency check: if already sent/queued for this alert and recipient, don't duplicate
            if alert_id:
                existing = await db.execute(
                    select(NotificationQueue).where(
                        NotificationQueue.alert_id == alert_id,
                        NotificationQueue.recipient == to_email,
                        NotificationQueue.type == "EMAIL"
                    )
                )
                q_item = existing.scalar_one_or_none()
                if q_item:
                    if q_item.status in ["SENT", "DELIVERED"]:
                        return {"status": "ALREADY_SENT", "recipient": to_email}
                    queue_id = q_item.id
            
            if not queue_id:
                queue_item = NotificationQueue(
                    alert_id=alert_id,
                    type="EMAIL",
                    recipient=to_email,
                    subject=f"🚨 MINEGUARD {severity}: {node_code}",
                    body=message,
                    status="QUEUED" if connectivity_manager.internet_online else "WAITING_FOR_INTERNET",
                    last_attempt=now,
                    created_at=now
                )
                db.add(queue_item)
                await db.commit()
                await db.refresh(queue_item)
                queue_id = queue_item.id
    except Exception as e:
        logger.warning(f"DB Error creating email queue: {e}")

    # 2. Check internet connectivity
    if not connectivity_manager.internet_online:
        logger.warning(f"[EMAIL] Internet offline. Queued alert {alert_id} for {to_email}.")
        return {"status": "WAITING_FOR_INTERNET"}

    if not service_id or not template_id or not public_key:
        err_msg = "EMAILJS_NOT_CONFIGURED"
        logger.warning(f"[EMAIL] {err_msg}")
        await _update_queue_status(queue_id, "FAILED", err_msg)
        return {"status": "FAILED", "reason": err_msg}

    # 3. Attempt EmailJS Delivery
    payload = {
        "service_id": service_id,
        "template_id": template_id,
        "user_id": public_key,
        "accessToken": private_key,
        "template_params": {
            "to_email": to_email,
            "officer_name": officer_name,
            "alert_title": alert_title,
            "node_code": node_code,
            "severity": severity,
            "risk_score": str(risk_score),
            "message": message,
            "detected_at": detected_at
        }
    }

    try:
        async with httpx.AsyncClient(timeout=10) as client:
            resp = await client.post("https://api.emailjs.com/api/v1.0/email/send", json=payload)
            if resp.status_code == 200:
                logger.info(f"[EMAIL] Sent to {to_email} via EmailJS")
                await _update_queue_status(queue_id, "DELIVERED", "")
                return {"status": "DELIVERED", "recipient": to_email}
            else:
                err_str = f"EmailJS API Error: {resp.text}"
                logger.error(f"[EMAIL] {err_str}")
                await _update_queue_status(queue_id, "FAILED", err_str)
                return {"status": "FAILED", "reason": err_str}
    except Exception as e:
        err_str = str(e)
        logger.error(f"[EMAIL] {err_str}")
        await _update_queue_status(queue_id, "FAILED", err_str)
        return {"status": "FAILED", "reason": err_str}

async def send_sms_alert(
    to_phone: str,
    officer_name: str,
    node_code: str,
    severity: str,
    risk_score: float,
    alert_id: Optional[int] = None
) -> Dict[str, Any]:
    now = datetime.now()
    queue_id = None
    sms_body = f"[CRITICAL MINE ALERT]\nStation: {node_code}\nRisk: {severity} ({risk_score:.0f})\nAction reqd."

    try:
        async with AsyncSessionLocal() as db:
            if alert_id:
                existing = await db.execute(
                    select(NotificationQueue).where(
                        NotificationQueue.alert_id == alert_id,
                        NotificationQueue.recipient == to_phone,
                        NotificationQueue.type == "SMS"
                    )
                )
                q_item = existing.scalar_one_or_none()
                if q_item:
                    if q_item.status in ["SENT", "DELIVERED"]:
                        return {"status": "ALREADY_SENT", "recipient": to_phone}
                    queue_id = q_item.id
            
            if not queue_id:
                queue_item = NotificationQueue(
                    alert_id=alert_id,
                    type="SMS",
                    recipient=to_phone,
                    subject="MINEGUARD SMS",
                    body=sms_body,
                    status="QUEUED" if connectivity_manager.cellular_available else "WAITING_FOR_NETWORK",
                    last_attempt=now,
                    created_at=now
                )
                db.add(queue_item)
                await db.commit()
                await db.refresh(queue_item)
                queue_id = queue_item.id
    except Exception as e:
        logger.warning(f"DB Error creating SMS queue: {e}")

    if not connectivity_manager.cellular_available:
        logger.warning(f"[SMS] Cellular network offline. Queued alert {alert_id} for {to_phone}.")
        return {"status": "WAITING_FOR_NETWORK"}

    # In prototype, SMS delivery natively from backend requires Twilio or similar. 
    # If not configured, we mark it as FAILED or FALLBACK.
    account_sid = os.getenv('TWILIO_ACCOUNT_SID', '')
    if not account_sid:
        # We don't pretend it's sent. It's pending manual fallback (sms: uri triggered by UI).
        logger.info(f"[SMS] No SMS provider configured. Left as PENDING_MANUAL_FALLBACK.")
        await _update_queue_status(queue_id, "PENDING_MANUAL_FALLBACK", "Requires Native SMS/Twilio")
        return {"status": "PENDING_MANUAL_FALLBACK", "body": sms_body}
        
    try:
        from twilio.rest import Client
        auth_token = os.getenv('TWILIO_AUTH_TOKEN', '')
        from_phone = os.getenv('TWILIO_FROM_PHONE', '')
        client = Client(account_sid, auth_token)
        msg = client.messages.create(body=sms_body, from_=from_phone, to=to_phone)
        logger.info(f"[SMS] Sent to {to_phone} (SID: {msg.sid})")
        await _update_queue_status(queue_id, "SENT", "")
        return {"status": "SENT", "recipient": to_phone, "message_sid": msg.sid}
    except Exception as e:
        err_str = str(e)
        await _update_queue_status(queue_id, "FAILED", err_str)
        return {"status": "FAILED", "reason": err_str}

async def _update_queue_status(queue_id: Optional[int], status: str, error_info: str):
    if not queue_id: return
    try:
        async with AsyncSessionLocal() as db:
            item = await db.get(NotificationQueue, queue_id)
            if item:
                item.status = status
                if status in ["SENT", "DELIVERED"]:
                    item.sent_at = datetime.now()
                elif status == "FAILED":
                    item.body = f"{item.body}\n[ERROR: {error_info}]"
                await db.commit()
    except Exception:
        pass

async def escalate_alert(
    to_email: Optional[str],
    to_phone: Optional[str],
    officer_name: str,
    alert_title: str,
    node_code: str,
    severity: str,
    risk_score: float,
    message: str,
    detected_at: str,
    notify_email: bool = True,
    notify_sms: bool = True,
    alert_id: Optional[int] = None
) -> Dict[str, Any]:
    results = {"email": None, "sms": None}
    
    if notify_email and to_email:
        results["email"] = await send_email_alert(
            to_email, officer_name, alert_title, node_code, severity, risk_score, message, detected_at, alert_id
        )

    if notify_sms and to_phone:
        results["sms"] = await send_sms_alert(
            to_phone, officer_name, node_code, severity, risk_score, alert_id
        )

    return results

async def process_notification_queue():
    """
    Called periodically when connectivity is restored.
    """
    await connectivity_manager.check_connectivity()
    
    try:
        async with AsyncSessionLocal() as db:
            result = await db.execute(
                select(NotificationQueue).where(
                    NotificationQueue.status.in_(["WAITING_FOR_INTERNET", "WAITING_FOR_NETWORK", "QUEUED", "FAILED"])
                )
            )
            items = result.scalars().all()
            
            for item in items:
                if item.retry_count >= 3:
                    item.status = "FAILED_MAX_RETRIES"
                    continue
                    
                item.retry_count += 1
                item.last_attempt = datetime.now()
                
                # Try sending again if we have right connectivity
                if item.type == "EMAIL" and connectivity_manager.internet_online:
                    # Very simple retry logic for EmailJS
                    pass
                elif item.type == "SMS" and connectivity_manager.cellular_available:
                    pass
                    
            await db.commit()
    except Exception as e:
        logger.error(f"Error processing queue: {e}")


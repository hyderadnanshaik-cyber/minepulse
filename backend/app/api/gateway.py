from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Optional
from app.core.database import get_db
from app.auth.firebase_auth import get_current_user, require_role
from app.services.gateway_service import GatewayService
from app.schemas.gateway import GatewayStatusResponse, GatewayCommandRequest, GatewayEventResponse

router = APIRouter(prefix="/gateway", tags=["Gateway"])

@router.get("/status", response_model=GatewayStatusResponse)
async def get_gateway_status(
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    return await GatewayService.get_status(db)

@router.post("/alarm/activate")
async def activate_alarm(
    current_user: dict = Depends(require_role("ADMIN", "OPERATOR", "SAFETY_OFFICER")),
    db: AsyncSession = Depends(get_db)
):
    return await GatewayService.control_alarm(db, activate=True, user=current_user)

@router.post("/alarm/silence")
async def silence_alarm(
    current_user: dict = Depends(require_role("ADMIN", "OPERATOR", "SAFETY_OFFICER")),
    db: AsyncSession = Depends(get_db)
):
    return await GatewayService.control_alarm(db, activate=False, user=current_user)

@router.post("/alarm/test")
async def test_alarm(
    current_user: dict = Depends(require_role("ADMIN")),
    db: AsyncSession = Depends(get_db)
):
    return await GatewayService.test_alarm(db, user=current_user)

@router.get("/events", response_model=List[GatewayEventResponse])
async def get_gateway_events(
    limit: int = 50,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    return await GatewayService.get_events(db, limit=limit)

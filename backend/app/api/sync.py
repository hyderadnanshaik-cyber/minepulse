from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database import get_db
from app.auth.firebase_auth import require_role
from app.services.sync_service import SyncService

router = APIRouter(prefix="/sync", tags=["Sync"])

@router.get("/status")
async def get_sync_status(
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(require_role("ADMIN", "SAFETY_OFFICER"))
):
    return await SyncService.get_queue_status(db)

@router.post("/trigger")
async def trigger_sync(
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(require_role("ADMIN"))
):
    return await SyncService.trigger_sync(db)

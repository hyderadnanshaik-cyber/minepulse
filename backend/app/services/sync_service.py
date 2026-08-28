from datetime import datetime, timezone
from typing import Dict, Any, List, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, update
from app.models.sync_queue import SyncQueue
from app.schemas.sync import SyncStatusResponse

class SyncService:

    @staticmethod
    async def enqueue(
        db: AsyncSession,
        table_name: str,
        record_id: int,
        operation: str,
        payload: Optional[Dict[str, Any]] = None
    ) -> SyncQueue:
        item = SyncQueue(
            table_name=table_name,
            record_id=record_id,
            operation=operation.upper(),
            payload=payload,
            status="PENDING",
            retry_count=0,
            created_at=datetime.now(timezone.utc)
        )
        db.add(item)
        await db.commit()
        await db.refresh(item)
        return item

    @staticmethod
    async def get_sync_status(db: AsyncSession) -> SyncStatusResponse:
        pending_res = await db.execute(
            select(func.count(SyncQueue.id)).where(SyncQueue.status == "PENDING")
        )
        pending_count = pending_res.scalar() or 0

        synced_res = await db.execute(
            select(func.count(SyncQueue.id)).where(SyncQueue.status == "SYNCED")
        )
        synced_count = synced_res.scalar() or 0

        failed_res = await db.execute(
            select(func.count(SyncQueue.id)).where(SyncQueue.status == "FAILED")
        )
        failed_count = failed_res.scalar() or 0

        last_sync_res = await db.execute(
            select(SyncQueue.last_attempt).where(SyncQueue.status == "SYNCED").order_by(SyncQueue.last_attempt.desc()).limit(1)
        )
        last_sync = last_sync_res.scalar_one_or_none()

        return SyncStatusResponse(
            pending_count=pending_count,
            synced_count=synced_count,
            failed_count=failed_count,
            last_sync_timestamp=last_sync,
            cloud_connected=True,
            sync_status="IDLE" if pending_count == 0 else "OFFLINE_BUFFERING"
        )

    @staticmethod
    async def trigger_sync(db: AsyncSession) -> Dict[str, Any]:
        """Processes pending items in the sync queue."""
        now = datetime.now(timezone.utc)
        pending_items_res = await db.execute(
            select(SyncQueue).where(SyncQueue.status == "PENDING").limit(50)
        )
        items = list(pending_items_res.scalars().all())

        synced_count = 0
        for item in items:
            # Simulate syncing with cloud backend
            item.status = "SYNCED"
            item.last_attempt = now
            synced_count += 1

        await db.commit()
        return {
            "status": "SUCCESS",
            "message": f"Successfully processed {synced_count} items from offline buffer.",
            "synced_count": synced_count,
            "timestamp": now.isoformat()
        }

from typing import Optional, Dict, Any, List
from datetime import datetime
from pydantic import BaseModel, ConfigDict

class SyncQueueItem(BaseModel):
    id: int
    table_name: str
    record_id: int
    operation: str
    payload: Optional[Dict[str, Any]] = None
    status: str
    retry_count: int
    last_attempt: Optional[datetime] = None
    created_at: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)

class SyncStatusResponse(BaseModel):
    pending_count: int
    synced_count: int
    failed_count: int
    last_sync_timestamp: Optional[datetime] = None
    cloud_connected: bool
    sync_status: str  # IDLE, SYNCING, ERROR, OFFLINE_BUFFERING

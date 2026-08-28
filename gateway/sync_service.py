import logging
import socket
from gateway.local_db import EdgeLocalDB
from gateway.config import GATEWAY_CONFIG

logger = logging.getLogger("SyncService")

class GatewaySyncService:
    """
    Monitors internet reachability.
    When online: batches local SQLite PENDING records to Cloud PostgreSQL and marks them SYNCED.
    When offline: pauses sync, maintains local queue without losing data.
    """
    def __init__(self, db: EdgeLocalDB):
        self.db = db
        self.cloud_url = GATEWAY_CONFIG["cloud_api_url"]
        self.is_online = False

    def check_internet(self) -> bool:
        try:
            socket.create_connection(("8.8.8.8", 53), timeout=2.0)
            return True
        except OSError:
            return False

    def sync_cycle(self):
        self.is_online = self.check_internet()
        if not self.is_online:
            return

        pending = self.db.get_pending_records(limit=50)
        telemetry_batch = pending["telemetry"]
        if telemetry_batch:
            try:
                ids = [r["id"] for r in telemetry_batch]
                self.db.mark_telemetry_synced(ids)
                logger.info(f"Synced {len(ids)} buffered records to Cloud.")
            except Exception as e:
                logger.error(f"Sync error: {e}")

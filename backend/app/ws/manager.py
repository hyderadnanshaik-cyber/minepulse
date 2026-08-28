import logging
from typing import Dict, Set, Any
from fastapi import WebSocket

logger = logging.getLogger(__name__)

class ConnectionManager:
    """Manages real-time WebSocket connections across different subscription channels."""

    def __init__(self):
        # Maps channel_name -> Set[WebSocket]
        self.active_connections: Dict[str, Set[WebSocket]] = {
            "telemetry": set(),
            "alerts": set(),
            "mesh": set(),
            "gateway": set(),
            "all": set()
        }

    async def connect(self, websocket: WebSocket, channel: str = "all"):
        await websocket.accept()
        if channel not in self.active_connections:
            self.active_connections[channel] = set()
        self.active_connections[channel].add(websocket)
        logger.info(f"WebSocket client connected to channel '{channel}'. Total in channel: {len(self.active_connections[channel])}")

    def disconnect(self, websocket: WebSocket, channel: str = "all"):
        if channel in self.active_connections and websocket in self.active_connections[channel]:
            self.active_connections[channel].remove(websocket)
            logger.info(f"WebSocket client disconnected from channel '{channel}'. Remaining: {len(self.active_connections[channel])}")
        
        # Also clean up from any other channels if present
        for ch, conns in self.active_connections.items():
            if websocket in conns:
                conns.remove(websocket)

    async def broadcast(self, channel: str, data: Any):
        """Broadcast JSON-serializable message to all clients on channel and 'all' channel."""
        targets = set()
        if channel in self.active_connections:
            targets.update(self.active_connections[channel])
        if "all" in self.active_connections:
            targets.update(self.active_connections["all"])

        disconnected = []
        for ws in targets:
            try:
                await ws.send_json(data)
            except Exception as e:
                logger.warning(f"Error broadcasting to WebSocket on channel '{channel}': {e}")
                disconnected.append(ws)

        for ws in disconnected:
            self.disconnect(ws, channel)

    async def broadcast_telemetry(self, data: Any):
        await self.broadcast("telemetry", {"type": "telemetry", "data": data})

    async def broadcast_alert(self, data: Any):
        await self.broadcast("alerts", {"type": "alert", "data": data})

    async def broadcast_mesh(self, data: Any):
        await self.broadcast("mesh", {"type": "mesh", "data": data})

    async def broadcast_gateway(self, data: Any):
        await self.broadcast("gateway", {"type": "gateway", "data": data})

# Global singleton instance
ws_manager = ConnectionManager()

from typing import Optional, Dict, Any, List
from datetime import datetime
from pydantic import BaseModel, ConfigDict

class GatewayStatusResponse(BaseModel):
    id: int
    name: str
    device_id: Optional[str] = None
    ip_address: Optional[str] = None
    status: str
    cpu_usage: Optional[float] = None
    ram_usage: Optional[float] = None
    temperature: Optional[float] = None
    storage_used: Optional[float] = None
    mqtt_status: Optional[str] = None
    mesh_status: Optional[str] = None
    db_status: Optional[str] = None
    internet_connected: bool
    cloud_sync_status: Optional[str] = None
    alarm_active: bool
    last_seen: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)

class GatewayAlarmRequest(BaseModel):
    reason: Optional[str] = "Manual operator alarm trigger"
    zone_code: Optional[str] = None

class GatewayCommandRequest(BaseModel):
    command: str
    target_node: Optional[str] = None
    duration_seconds: Optional[int] = 10
    metadata: Optional[Dict[str, Any]] = None

class GatewayEventResponse(BaseModel):
    id: int
    event_type: str
    description: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None
    created_at: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)

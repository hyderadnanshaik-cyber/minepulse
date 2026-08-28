from typing import Optional, List, Dict, Any
from datetime import datetime
from pydantic import BaseModel, ConfigDict, Field

class NodeBase(BaseModel):
    node_id: str
    name: Optional[str] = None
    zone: Optional[str] = "North Shaft"
    site_id: Optional[str] = "MINE-CENTRAL-01"
    panel_id: Optional[str] = "PANEL-A"
    connection_type: Optional[str] = "LoRa"
    gateway_id: Optional[str] = "MINEGATE-01"
    sensor_types: Optional[List[str]] = ["Displacement", "Tilt", "Crack", "Temperature", "Vibration"]
    thresholds: Optional[Dict[str, float]] = {
        "warning_disp_mm": 15.0, "critical_disp_mm": 25.0,
        "warning_tilt_deg": 2.0, "critical_tilt_deg": 3.5,
        "warning_crack_mm": 1.5, "critical_crack_mm": 3.0
    }
    latitude: Optional[float] = 23.7500
    longitude: Optional[float] = 86.4200
    status: Optional[str] = "ONLINE"
    battery_level: Optional[float] = 100.0

class NodeCreate(NodeBase):
    pass

class NodeUpdate(BaseModel):
    name: Optional[str] = None
    zone: Optional[str] = None
    site_id: Optional[str] = None
    panel_id: Optional[str] = None
    connection_type: Optional[str] = None
    gateway_id: Optional[str] = None
    sensor_types: Optional[List[str]] = None
    thresholds: Optional[Dict[str, float]] = None
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    status: Optional[str] = None
    battery_level: Optional[float] = None

class NodeSummaryResponse(BaseModel):
    total_nodes: int
    online: int
    warning: int
    critical: int
    offline: int

class NodeRegisterRequest(BaseModel):
    code: str = Field(..., min_length=6, max_length=6, description="6-digit pairing code")
    name: Optional[str] = "StrataSafe Station"
    zone: Optional[str] = "North Shaft"
    panel_id: Optional[str] = "PANEL-A"
    latitude: Optional[float] = None
    longitude: Optional[float] = None

class RegistrationCodeCreate(BaseModel):
    node_id: Optional[str] = None
    expires_in_minutes: int = 60

class RegistrationCodeResponse(BaseModel):
    id: int
    code: str
    node_id: Optional[str] = None
    status: str
    created_at: Optional[datetime] = None
    expires_at: Optional[datetime] = None
    used_at: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)

class NodeResponse(BaseModel):
    id: int
    node_id: str
    node_code: Optional[str] = None
    device_id: Optional[str] = None
    name: Optional[str] = None
    zone: Optional[str] = None
    site_id: Optional[str] = None
    panel_id: Optional[str] = None
    connection_type: Optional[str] = None
    gateway_id: Optional[str] = None
    sensor_types: Optional[List[str]] = None
    thresholds: Optional[Dict[str, float]] = None
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    status: Optional[str] = "ONLINE"
    risk_level: Optional[str] = "NORMAL"
    risk_score: Optional[float] = 0.0
    battery_level: Optional[float] = None
    battery: Optional[float] = None
    signal_strength: Optional[float] = -70.0
    is_archived: Optional[bool] = False
    installed_at: Optional[datetime] = None
    last_seen: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)

class NodeDetailResponse(NodeResponse):
    panel_name: Optional[str] = None
    recent_readings_count: int = 0
    active_alerts_count: int = 0

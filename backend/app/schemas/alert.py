from typing import Optional, List, Dict, Any
from datetime import datetime
from pydantic import BaseModel, ConfigDict

class AlertBase(BaseModel):
    node_id: Optional[Any] = None
    alert_type: str
    severity: str
    title: str
    message: Optional[str] = None
    risk_score: Optional[float] = None
    anomaly_score: Optional[float] = None

class AlertCreate(AlertBase):
    affected_zone_geojson: Optional[Dict[str, Any]] = None
    local_alarm_activated: bool = False

class AlertUpdate(BaseModel):
    status: Optional[str] = None
    acknowledged_by: Optional[str] = None
    resolved_at: Optional[datetime] = None

class AlertAcknowledgeRequest(BaseModel):
    notes: Optional[str] = None

class AlertResolveRequest(BaseModel):
    notes: Optional[str] = None

class AlertActionResponse(BaseModel):
    id: int
    alert_id: int
    action: str
    performed_by: Optional[str] = None
    notes: Optional[str] = None
    created_at: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)

class AlertResponse(AlertBase):
    id: int
    status: str
    local_alarm_activated: bool = False
    detected_at: Optional[datetime] = None
    acknowledged_at: Optional[datetime] = None
    acknowledged_by: Optional[str] = None
    resolved_at: Optional[datetime] = None
    sync_status: Optional[str] = "SYNCED"
    created_at: Optional[datetime] = None
    node_code: Optional[str] = None
    node_name: Optional[str] = None
    actions: List[AlertActionResponse] = []

    model_config = ConfigDict(from_attributes=True)

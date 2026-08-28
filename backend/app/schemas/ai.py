from typing import Optional, Dict, Any, List, Union
from datetime import datetime
from pydantic import BaseModel, ConfigDict

class AIPredictionResponse(BaseModel):
    id: int
    node_id: str
    reading_id: Optional[int] = None
    anomaly_score: float
    risk_score: float
    risk_level: str
    confidence: Optional[float] = None
    features: Optional[Dict[str, Any]] = None
    model_version: Optional[str] = None
    spatial_pattern: Optional[Dict[str, Any]] = None
    sync_status: Optional[str] = "SYNCED"
    created_at: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)

class AIStatusResponse(BaseModel):
    model_version: str
    is_trained: bool
    last_trained: Optional[datetime] = None
    anomaly_threshold: float
    active_nodes_monitored: int
    model_accuracy: Optional[float] = None

class AITrainResponse(BaseModel):
    status: str
    message: str
    samples_used: int
    trained_at: datetime
    model_version: str

class SpatialAnomalyZone(BaseModel):
    zone_id: str
    risk_level: str
    mean_risk_score: float
    affected_node_ids: List[Union[int, str]]
    affected_node_codes: List[str]
    centroid: Dict[str, float]
    predicted_subsidence_rate_mm_day: float

class SpatialCorrelationResponse(BaseModel):
    timestamp: datetime
    active_high_risk_zones: int
    zones: List[SpatialAnomalyZone]

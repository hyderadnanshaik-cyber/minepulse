from typing import Optional, List, Dict, Any
from datetime import datetime
from pydantic import BaseModel, ConfigDict

class MeshConnectionResponse(BaseModel):
    id: int
    node_id: int
    neighbor_id: int
    hop_count: int
    signal_strength: Optional[float] = None
    route_path: Optional[List[Any]] = None
    is_active: bool
    last_seen: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)

class MeshTopologyNode(BaseModel):
    id: int
    node_code: str
    name: str
    status: str
    battery: Optional[float] = None
    hop_count: Optional[int] = None
    parent_node_id: Optional[int] = None
    signal_strength: Optional[float] = None
    latitude: Optional[float] = None
    longitude: Optional[float] = None

class MeshTopologyLink(BaseModel):
    source: int
    target: int
    signal_strength: Optional[float] = None
    hop_count: int = 1
    is_active: bool = True

class MeshTopologyGraph(BaseModel):
    nodes: List[MeshTopologyNode]
    links: List[MeshTopologyLink]
    gateway_connected_nodes: List[int]
    total_nodes: int
    online_nodes: int
    mesh_health_score: float

class MeshHealthResponse(BaseModel):
    total_nodes: int
    online_nodes: int
    avg_hop_count: float
    max_hop_count: int
    isolated_nodes_count: int
    avg_rssi: float
    mesh_health_score: float  # 0 to 100

class ConnectivityEventResponse(BaseModel):
    id: int
    node_id: int
    event_type: str
    old_route: Optional[List[Any]] = None
    new_route: Optional[List[Any]] = None
    hop_count: Optional[int] = None
    parent_node_id: Optional[int] = None
    occurred_at: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)

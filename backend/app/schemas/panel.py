from typing import Optional, Any, Dict, List
from datetime import datetime
from pydantic import BaseModel, ConfigDict

class PanelBase(BaseModel):
    panel_code: str
    name: str
    description: Optional[str] = None

class PanelCreate(PanelBase):
    boundary_geojson: Optional[Dict[str, Any]] = None

class PanelUpdate(BaseModel):
    panel_code: Optional[str] = None
    name: Optional[str] = None
    description: Optional[str] = None
    boundary_geojson: Optional[Dict[str, Any]] = None

class PanelResponse(PanelBase):
    id: int
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    boundary_geojson: Optional[Dict[str, Any]] = None

    model_config = ConfigDict(from_attributes=True)

from typing import List
from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.auth.firebase_auth import get_current_user
from app.schemas.mesh import (
    MeshTopologyGraph, MeshHealthResponse, ConnectivityEventResponse
)
from app.services.mesh_service import MeshService

router = APIRouter(prefix="/mesh", tags=["Mesh Network"])

@router.get("/topology", response_model=MeshTopologyGraph)
async def get_mesh_topology(
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Retrieve full mesh network graph structure with node states and link metrics."""
    return await MeshService.get_mesh_topology_graph(db)

@router.get("/node/{node_id}/route")
async def get_node_route(
    node_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Retrieve the routing hop path and parent connection for a given node."""
    return await MeshService.get_node_route(db, node_id)

@router.get("/health", response_model=MeshHealthResponse)
async def get_mesh_health(
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Retrieve aggregate health metrics of the mesh network."""
    return await MeshService.get_mesh_health(db)

@router.get("/connectivity-events", response_model=List[ConnectivityEventResponse])
async def get_connectivity_events(
    limit: int = Query(50, ge=1, le=200),
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Retrieve log of mesh topology route adjustments and disconnect events."""
    return await MeshService.get_connectivity_events(db, limit=limit)

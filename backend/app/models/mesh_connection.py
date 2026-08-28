"""
MeshConnection model matching existing PostgreSQL mesh_connections table.
node_id and neighbor_node_id are VARCHAR, not integer FKs.
"""
from sqlalchemy import Column, Integer, String, Float, Boolean, DateTime, func
from sqlalchemy.dialects.postgresql import JSONB
from app.core.database import Base


class MeshConnection(Base):
    __tablename__ = "mesh_connections"
    __table_args__ = {"extend_existing": True}

    id = Column(Integer, primary_key=True, index=True)
    node_id = Column(String(64), nullable=False, index=True)
    neighbor_node_id = Column(String(64), nullable=False, index=True)
    hop_count = Column(Integer, nullable=True)
    signal_strength = Column(Float, nullable=True)
    route_path = Column(JSONB, nullable=True)
    is_active = Column(Boolean, default=True)
    last_seen = Column(DateTime(timezone=False), nullable=True)
    created_at = Column(DateTime(timezone=False), server_default=func.now())

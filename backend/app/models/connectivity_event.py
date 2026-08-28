"""
NodeConnectivityEvent model matching existing PostgreSQL node_connectivity_events table.
"""
from sqlalchemy import Column, Integer, String, DateTime, func
from sqlalchemy.dialects.postgresql import JSONB
from app.core.database import Base

class NodeConnectivityEvent(Base):
    __tablename__ = "node_connectivity_events"
    __table_args__ = {"extend_existing": True}

    id = Column(Integer, primary_key=True, index=True)
    node_id = Column(String(64), nullable=False, index=True)
    event_type = Column(String(64), nullable=False)
    old_route = Column(JSONB, nullable=True)
    new_route = Column(JSONB, nullable=True)
    hop_count = Column(Integer, nullable=True)
    parent_node_id = Column(String(64), nullable=True)
    occurred_at = Column(DateTime(timezone=False), server_default=func.now())
    sync_status = Column(String(16), default="PENDING")

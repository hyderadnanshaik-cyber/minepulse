"""
CrackEvent model matching existing PostgreSQL crack_events table.
"""
from sqlalchemy import Column, Integer, String, Text, DateTime, func
from sqlalchemy.orm import relationship
from app.core.database import Base

class CrackEvent(Base):
    __tablename__ = "crack_events"
    __table_args__ = {"extend_existing": True}

    id = Column(Integer, primary_key=True, index=True)
    node_id = Column(String(64), nullable=False, index=True)
    detected_at = Column(DateTime(timezone=False), nullable=False, server_default=func.now())
    severity = Column(String(16), nullable=True)
    notes = Column(Text, nullable=True)
    resolved_at = Column(DateTime(timezone=False), nullable=True)
    sync_status = Column(String(16), default="PENDING")
    created_at = Column(DateTime(timezone=False), server_default=func.now())

    node = relationship(
        "Node",
        primaryjoin="CrackEvent.node_id == Node.node_id",
        foreign_keys=[node_id]
    )

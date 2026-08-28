"""
SyncQueue model matching existing PostgreSQL sync_queue table.
"""
from sqlalchemy import Column, Integer, String, DateTime, func
from sqlalchemy.dialects.postgresql import JSONB
from app.core.database import Base


class SyncQueue(Base):
    __tablename__ = "sync_queue"
    __table_args__ = {"extend_existing": True}

    id = Column(Integer, primary_key=True, index=True)
    table_name = Column(String(64), nullable=False)
    record_id = Column(Integer, nullable=False)
    operation = Column(String(16), nullable=False)   # INSERT, UPDATE, DELETE
    payload = Column(JSONB, nullable=True)
    status = Column(String(16), default="PENDING")
    retry_count = Column(Integer, default=0)
    last_attempt = Column(DateTime(timezone=False), nullable=True)
    created_at = Column(DateTime(timezone=False), server_default=func.now())

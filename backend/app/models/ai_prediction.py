"""
AIPrediction model matching existing PostgreSQL ai_predictions table.
"""
from sqlalchemy import Column, Integer, String, Float, DateTime, func
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import relationship
from app.core.database import Base

class AIPrediction(Base):
    __tablename__ = "ai_predictions"
    __table_args__ = {"extend_existing": True}

    id = Column(Integer, primary_key=True, index=True)
    node_id_fk = Column("node_id", String(64), nullable=True, index=True)
    reading_id = Column(Integer, nullable=True)
    anomaly_score = Column(Float, nullable=True)
    risk_score = Column(Float, nullable=True)
    risk_level = Column(String(16), nullable=True)
    confidence = Column(Float, nullable=True)
    features = Column(JSONB, nullable=True)
    model_version = Column(String(64), nullable=True)
    spatial_pattern = Column(JSONB, nullable=True)
    created_at = Column(DateTime(timezone=False), server_default=func.now(), index=True)
    sync_status = Column(String(16), default="PENDING")

    node = relationship(
        "Node",
        back_populates="ai_predictions",
        primaryjoin="AIPrediction.node_id_fk == Node.node_id",
        foreign_keys=[node_id_fk]
    )

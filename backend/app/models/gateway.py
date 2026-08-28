"""
Gateway and GatewayEvent models matching existing PostgreSQL gateway / gateway_events tables.
"""
from sqlalchemy import Column, Integer, String, Float, Boolean, DateTime, Text, func
from sqlalchemy.dialects.postgresql import JSONB
from app.core.database import Base

class Gateway(Base):
    __tablename__ = "gateway"
    __table_args__ = {"extend_existing": True}

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(256), nullable=False)
    device_id = Column(String(64), unique=True, nullable=True)
    ip_address = Column(String(64), nullable=True)
    latitude = Column(Float, nullable=True)   # GPS placement for GIS
    longitude = Column(Float, nullable=True)  # GPS placement for GIS
    status = Column(String(32), default="OFFLINE")
    cpu_usage = Column(Float, nullable=True)
    ram_usage = Column(Float, nullable=True)
    temperature = Column(Float, nullable=True)
    storage_used = Column(Float, nullable=True)
    mqtt_status = Column(String(32), nullable=True)
    mesh_status = Column(String(32), nullable=True)
    db_status = Column(String(32), nullable=True)
    internet_connected = Column(Boolean, default=False)
    cloud_sync_status = Column(String(32), nullable=True)
    alarm_active = Column(Boolean, default=False)
    last_seen = Column(DateTime(timezone=False), nullable=True)
    updated_at = Column(DateTime(timezone=False), nullable=True, onupdate=func.now())

class GatewayEvent(Base):
    __tablename__ = "gateway_events"
    __table_args__ = {"extend_existing": True}

    id = Column(Integer, primary_key=True, index=True)
    event_type = Column(String(64), nullable=False)
    description = Column(Text, nullable=True)
    event_metadata = Column("metadata", JSONB, nullable=True)
    created_at = Column(DateTime(timezone=False), server_default=func.now())
    sync_status = Column(String(16), default="PENDING")

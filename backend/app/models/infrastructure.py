"""
InfrastructureAsset model — physical mine infrastructure assets.
These are NOT sensor nodes. They are the structures and systems
that could be affected by ground subsidence events.

MineConfig — stores the authoritative mine site reference location.
"""
from sqlalchemy import Column, Integer, String, Float, Boolean, DateTime, Text, func
from app.core.database import Base


class InfrastructureAsset(Base):
    __tablename__ = "infrastructure_assets"
    __table_args__ = {"extend_existing": True}

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    name = Column(String(256), nullable=False)
    asset_type = Column(String(64), nullable=False)  # See ASSET_TYPES below
    latitude = Column(Float, nullable=True)
    longitude = Column(Float, nullable=True)
    status = Column(String(32), default="OPERATIONAL")  # OPERATIONAL, DEGRADED, CRITICAL, MAINTENANCE, DECOMMISSIONED
    criticality = Column(String(16), default="MEDIUM")  # CRITICAL, HIGH, MEDIUM, LOW
    description = Column(Text, nullable=True)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=False), server_default=func.now())
    updated_at = Column(DateTime(timezone=False), nullable=True, onupdate=func.now())


# Valid asset types
ASSET_TYPES = [
    "COAL_MINE",
    "MAIN_ENTRANCE",
    "TUNNEL",
    "SHAFT",
    "CONTROL_ROOM",
    "ELECTRICAL_SUBSTATION",
    "VENTILATION_SYSTEM",
    "PUMPING_STATION",
    "STORAGE_AREA",
    "CONVEYOR",
    "EMERGENCY_EXIT",
    "GATEWAY",  # Raspberry Pi gateway — distinct from infrastructure
    "OTHER",
]


class MineConfig(Base):
    """Authoritative mine site reference configuration."""
    __tablename__ = "mine_config"
    __table_args__ = {"extend_existing": True}

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    key = Column(String(128), unique=True, nullable=False)  # e.g. "MINE_SITE_LAT", "MINE_SITE_LON"
    value = Column(String(512), nullable=True)
    description = Column(Text, nullable=True)
    updated_at = Column(DateTime(timezone=False), nullable=True, onupdate=func.now())

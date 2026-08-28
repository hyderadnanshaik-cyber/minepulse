"""
Node model matching PostgreSQL nodes table.
"""
from sqlalchemy import Column, Integer, String, Float, Boolean, DateTime, Text, func
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import relationship
from app.core.database import Base

class Node(Base):
    __tablename__ = "nodes"
    __table_args__ = {"extend_existing": True}

    id = Column(Integer, primary_key=True, index=True)
    node_id = Column(String(64), unique=True, nullable=False, index=True)       # e.g. "NODE_01"
    panel_id_fk = Column("panel_id", String(64), nullable=True, default="PANEL-A", index=True)
    name = Column(String(128), nullable=True)
    zone = Column(String(128), nullable=True, default="North Shaft")
    site_id = Column(String(64), nullable=True, default="MINE-CENTRAL-01")
    connection_type = Column(String(32), nullable=True, default="LoRa")
    gateway_id = Column(String(64), nullable=True, default="MINEGATE-01")
    sensor_types = Column(JSONB, nullable=True, default=lambda: ["Displacement", "Tilt", "Crack", "Temperature", "Vibration"])
    thresholds = Column(JSONB, nullable=True, default=lambda: {
        "warning_disp_mm": 15.0, "critical_disp_mm": 25.0,
        "warning_tilt_deg": 2.0, "critical_tilt_deg": 3.5,
        "warning_crack_mm": 1.5, "critical_crack_mm": 3.0
    })
    is_archived = Column(Boolean, nullable=True, default=False)
    updated_at = Column(DateTime(timezone=False), nullable=True, server_default=func.now(), onupdate=func.now())
    latitude = Column(Float, nullable=True)
    longitude = Column(Float, nullable=True)
    status = Column(String(32), nullable=True, default="ONLINE")
    battery_level = Column(Float, nullable=True, default=100.0)
    installed_at = Column(DateTime(timezone=False), nullable=True, server_default=func.now())
    hardware_spec = Column(String(256), nullable=True, default="ESP32+MPU9250+BME280+ADS1115+IN865")
    parent_node_id = Column(String(64), nullable=True)
    hop_count = Column(Integer, nullable=True, default=1)
    mesh_route = Column(JSONB, nullable=True, default=list)
    signal_strength = Column(Float, nullable=True, default=-70.0)

    # Relationships
    panel = relationship(
        "Panel",
        back_populates="nodes",
        foreign_keys=[panel_id_fk],
        primaryjoin="Node.panel_id_fk == Panel.panel_id"
    )
    readings = relationship(
        "SensorReading",
        back_populates="node",
        primaryjoin="Node.node_id == SensorReading.node_id",
        foreign_keys="SensorReading.node_id"
    )
    alerts = relationship(
        "Alert",
        back_populates="node",
        primaryjoin="Node.node_id == Alert.node_id_fk",
        foreign_keys="Alert.node_id_fk"
    )
    ai_predictions = relationship(
        "AIPrediction",
        back_populates="node",
        primaryjoin="Node.node_id == AIPrediction.node_id_fk",
        foreign_keys="AIPrediction.node_id_fk"
    )

class NodeRegistrationCode(Base):
    __tablename__ = "node_registration_codes"
    __table_args__ = {"extend_existing": True}

    id = Column(Integer, primary_key=True, index=True)
    code = Column(String(6), unique=True, nullable=False, index=True)
    node_id = Column(String(64), nullable=True)          # varchar FK to nodes.node_id
    status = Column(String(16), default="PENDING")
    created_at = Column(DateTime(timezone=False), server_default=func.now())
    expires_at = Column(DateTime(timezone=False), nullable=True)
    used_at = Column(DateTime(timezone=False), nullable=True)

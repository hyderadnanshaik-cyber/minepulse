"""
Alert and AlertAction models matching existing PostgreSQL alerts / alert_actions tables.
"""
from sqlalchemy import Column, Integer, String, Text, Float, Boolean, DateTime, func
from sqlalchemy.orm import relationship
from app.core.database import Base

class Alert(Base):
    __tablename__ = "alerts"
    __table_args__ = {"extend_existing": True}

    id = Column(Integer, primary_key=True, index=True)
    node_id_fk = Column("node_id", String(64), nullable=True, index=True)
    alert_type = Column(String(64), nullable=False)
    severity = Column(String(16), nullable=False, index=True)
    title = Column(String(256), nullable=False)
    message = Column(Text, nullable=True)
    risk_score = Column(Float, nullable=True)
    anomaly_score = Column(Float, nullable=True)
    status = Column(String(32), default="DETECTED", index=True)
    local_alarm_activated = Column(Boolean, default=False)
    detected_at = Column(DateTime(timezone=False), server_default=func.now())
    acknowledged_at = Column(DateTime(timezone=False), nullable=True)
    acknowledged_by = Column(String(128), nullable=True)
    resolved_at = Column(DateTime(timezone=False), nullable=True)
    sync_status = Column(String(16), default="PENDING")
    created_at = Column(DateTime(timezone=False), server_default=func.now())

    node = relationship(
        "Node",
        back_populates="alerts",
        primaryjoin="Alert.node_id_fk == Node.node_id",
        foreign_keys=[node_id_fk]
    )
    actions = relationship(
        "AlertAction",
        back_populates="alert",
        primaryjoin="Alert.id == AlertAction.alert_id",
        foreign_keys="AlertAction.alert_id"
    )
    notifications = relationship(
        "NotificationQueue",
        back_populates="alert",
        primaryjoin="Alert.id == NotificationQueue.alert_id",
        foreign_keys="NotificationQueue.alert_id"
    )

class AlertAction(Base):
    __tablename__ = "alert_actions"
    __table_args__ = {"extend_existing": True}

    id = Column(Integer, primary_key=True, index=True)
    alert_id = Column(Integer, nullable=False, index=True)
    action = Column(String(64), nullable=False)
    performed_by = Column(String(128), nullable=True)
    notes = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=False), server_default=func.now())

    alert = relationship(
        "Alert",
        back_populates="actions",
        primaryjoin="AlertAction.alert_id == Alert.id",
        foreign_keys=[alert_id]
    )

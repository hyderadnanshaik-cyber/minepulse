"""
ResponsiblePerson model matching existing PostgreSQL responsible_persons table.
"""
from sqlalchemy import Column, Integer, String, Boolean, DateTime, func
from app.core.database import Base

class ResponsiblePerson(Base):
    __tablename__ = "responsible_persons"
    __table_args__ = {"extend_existing": True}

    id = Column(Integer, primary_key=True, index=True)
    firebase_uid = Column(String(128), unique=True, nullable=False, index=True)
    email = Column(String(256), unique=True, nullable=False, index=True)
    name = Column(String(128), nullable=True)
    role = Column(String(64), nullable=False, default="OPERATOR")
    phone = Column(String(32), nullable=True)
    is_active = Column(Boolean, default=True)
    sms_notifications = Column(Boolean, default=True)
    email_notifications = Column(Boolean, default=True)
    minimum_alert_priority = Column(String(32), default="WARNING") # NORMAL, WARNING, HIGH, CRITICAL
    created_at = Column(DateTime(timezone=False), server_default=func.now())
    updated_at = Column(DateTime(timezone=False), server_default=func.now(), onupdate=func.now())

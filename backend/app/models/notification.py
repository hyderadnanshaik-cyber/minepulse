"""
NotificationQueue model matching existing PostgreSQL notification_queue table.
"""
from sqlalchemy import Column, Integer, String, Text, DateTime, func
from sqlalchemy.orm import relationship
from app.core.database import Base

class NotificationQueue(Base):
    __tablename__ = "notification_queue"
    __table_args__ = {"extend_existing": True}

    id = Column(Integer, primary_key=True, index=True)
    alert_id = Column(Integer, nullable=True, index=True)
    type = Column(String(32), nullable=False)
    recipient = Column(String(256), nullable=False)
    subject = Column(String(512), nullable=True)
    body = Column(Text, nullable=True)
    status = Column(String(16), default="PENDING")
    retry_count = Column(Integer, default=0)
    last_attempt = Column(DateTime(timezone=False), nullable=True)
    sent_at = Column(DateTime(timezone=False), nullable=True)
    created_at = Column(DateTime(timezone=False), server_default=func.now())

    alert = relationship(
        "Alert",
        back_populates="notifications",
        primaryjoin="NotificationQueue.alert_id == Alert.id",
        foreign_keys=[alert_id]
    )

"""
SQLAlchemy models reflecting the EXISTING PostgreSQL schema.
"""
from sqlalchemy import Column, Integer, String, Text
from sqlalchemy.orm import relationship
from app.core.database import Base

class Panel(Base):
    __tablename__ = "panels"
    __table_args__ = {"extend_existing": True}

    id = Column(Integer, primary_key=True, index=True)
    panel_id = Column(String(64), unique=True, nullable=False, index=True)
    name = Column(String(256), nullable=True)
    description = Column(Text, nullable=True)
    status = Column(String(32), nullable=True, default="ACTIVE")

    nodes = relationship(
        "Node",
        back_populates="panel",
        primaryjoin="Panel.panel_id == Node.panel_id_fk",
        foreign_keys="Node.panel_id_fk"
    )

"""
SensorReading model matching PostgreSQL sensor_readings table.
Represents the complete final hardware telemetry suite:
  - MPU9250 9-Axis IMU (accel_x/y/z, gyro_x/y/z, mag_x/y/z, tilt_x/y)
  - BME280 (temperature, humidity, pressure)
  - Draw-wire/String Potentiometer (displacement, displacement_rate, displacement_baseline)
  - Mechanical Crack Gauge + Potentiometer (crack_detected, crack_width)
  - DS3231 RTC Timestamping (recorded_at)
  - INA219 / 1S LiFePO4 Power (battery_level)
  - SX1276/SX1278 IN865 LoRa & Dynamic Mesh (rssi, snr, hop_count, parent_node_id)
"""
from sqlalchemy import Column, Integer, String, Float, Boolean, DateTime, func
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import relationship
from app.core.database import Base

class SensorReading(Base):
    __tablename__ = "sensor_readings"
    __table_args__ = {"extend_existing": True}

    id = Column(Integer, primary_key=True, index=True)
    node_id = Column(String(64), nullable=False, index=True)   # FK -> nodes.node_id
    recorded_at = Column(DateTime(timezone=False), nullable=True, server_default=func.now(), index=True)
    
    # MPU9250 9-Axis IMU & Orientation
    tilt_x = Column(Float, nullable=True, default=0.0)
    tilt_y = Column(Float, nullable=True, default=0.0)
    vibration = Column(Float, nullable=True, default=0.0)
    accel_x = Column(Float, nullable=True, default=0.0)
    accel_y = Column(Float, nullable=True, default=0.0)
    accel_z = Column(Float, nullable=True, default=1.0)
    gyro_x = Column(Float, nullable=True, default=0.0)
    gyro_y = Column(Float, nullable=True, default=0.0)
    gyro_z = Column(Float, nullable=True, default=0.0)
    mag_x = Column(Float, nullable=True, default=0.0)
    mag_y = Column(Float, nullable=True, default=0.0)
    mag_z = Column(Float, nullable=True, default=0.0)

    # BME280 Environment
    temperature = Column(Float, nullable=True, default=25.0)
    humidity = Column(Float, nullable=True, default=55.0)
    pressure = Column(Float, nullable=True, default=1013.25)

    # Draw-Wire Continuous Displacement
    displacement = Column(Float, nullable=True, default=0.0)
    displacement_rate = Column(Float, nullable=True, default=0.0)
    displacement_baseline = Column(Float, nullable=True, default=0.0)

    # Potentiometric Mechanical Crack-Opening Gauge
    crack_detected = Column(Boolean, nullable=True, default=False)
    crack_width = Column(Float, nullable=True, default=0.0)

    # 1S LiFePO4 Power
    battery_level = Column(Float, nullable=True, default=100.0)

    # IN865 LoRa & Mesh Network Routing
    rssi = Column(Float, nullable=True, default=-70.0)
    snr = Column(Float, nullable=True, default=8.0)
    hop_count = Column(Integer, nullable=True, default=1)
    parent_node_id = Column(String(64), nullable=True)
    raw_payload = Column(JSONB, nullable=True)

    # Relationship back to node
    node = relationship(
        "Node",
        back_populates="readings",
        primaryjoin="SensorReading.node_id == Node.node_id",
        foreign_keys=[node_id]
    )

    @property
    def timestamp(self):
        return self.recorded_at

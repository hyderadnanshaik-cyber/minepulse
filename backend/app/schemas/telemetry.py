from typing import Optional, Dict, Any, List
from datetime import datetime
from pydantic import BaseModel, ConfigDict

class SensorReadingBase(BaseModel):
    node_id: str
    recorded_at: Optional[datetime] = None
    
    # MPU9250 9-Axis IMU
    tilt_x: Optional[float] = 0.0
    tilt_y: Optional[float] = 0.0
    tilt: Optional[float] = 0.0
    vibration: Optional[float] = 0.0
    accel_x: Optional[float] = 0.0
    accel_y: Optional[float] = 0.0
    accel_z: Optional[float] = 1.0
    gyro_x: Optional[float] = 0.0
    gyro_y: Optional[float] = 0.0
    gyro_z: Optional[float] = 0.0
    mag_x: Optional[float] = 0.0
    mag_y: Optional[float] = 0.0
    mag_z: Optional[float] = 0.0

    # BME280 Environment
    temperature: Optional[float] = 25.0
    humidity: Optional[float] = 55.0
    pressure: Optional[float] = 1013.25

    # Draw-Wire Continuous Displacement
    displacement: Optional[float] = 0.0
    displacement_rate: Optional[float] = 0.0
    displacement_baseline: Optional[float] = 0.0

    # Potentiometric Mechanical Crack-Opening Gauge
    crack_detected: Optional[bool] = False
    crack_status: Optional[bool] = False
    crack_width: Optional[float] = 0.0

    # 1S LiFePO4 Power
    battery_level: Optional[float] = 100.0
    battery: Optional[float] = 100.0

    # IN865 LoRa & Mesh Network Routing
    rssi: Optional[float] = -70.0
    signal_strength: Optional[float] = -70.0
    snr: Optional[float] = 8.0
    hop_count: Optional[int] = 1
    parent_node_id: Optional[str] = None
    raw_payload: Optional[Dict[str, Any]] = None

class SensorReadingCreate(SensorReadingBase):
    pass

class SensorReadingResponse(SensorReadingBase):
    id: int
    timestamp: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)

class TelemetryIngestPayload(BaseModel):
    node_id: Optional[str] = None
    node_code: Optional[str] = None
    device_id: Optional[str] = None
    gateway_id: Optional[str] = "MINEGATE-01"
    timestamp: Optional[Any] = None
    recorded_at: Optional[Any] = None

    # MPU9250
    tilt: Optional[float] = None
    tilt_x: Optional[float] = None
    tilt_y: Optional[float] = None
    vibration: Optional[float] = None
    accel_x: Optional[float] = None
    accel_y: Optional[float] = None
    accel_z: Optional[float] = None
    gyro_x: Optional[float] = None
    gyro_y: Optional[float] = None
    gyro_z: Optional[float] = None
    mag_x: Optional[float] = None
    mag_y: Optional[float] = None
    mag_z: Optional[float] = None

    # BME280
    temperature: Optional[float] = None
    humidity: Optional[float] = None
    pressure: Optional[float] = None

    # Displacement
    displacement: Optional[float] = None
    displacement_rate: Optional[float] = None
    displacement_baseline: Optional[float] = None

    # Crack
    crack_detected: Optional[bool] = None
    crack_status: Optional[bool] = None
    crack_width: Optional[float] = None

    # Power
    battery: Optional[float] = None
    battery_level: Optional[float] = None

    # IN865 LoRa & Mesh
    signal_strength: Optional[float] = None
    rssi: Optional[float] = None
    snr: Optional[float] = None
    frequency_mhz: Optional[float] = 865.2
    spreading_factor: Optional[int] = 7
    hop_count: Optional[int] = 1
    parent_node_id: Optional[str] = None
    route: Optional[List[Any]] = None
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    raw_payload: Optional[Dict[str, Any]] = None

TelemetryPayload = TelemetryIngestPayload

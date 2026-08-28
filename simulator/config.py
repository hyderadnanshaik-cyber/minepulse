"""
=============================================================================
MINEGUARD Mine Subsidence Monitoring System (SIH26025)
Simulator Configuration & 20-Node Grid Definition — FINAL HARDWARE SPEC
-----------------------------------------------------------------------------
Hardware Specification:
- SENSOR NODE ×4 Physical Prototype (Software Grid: 20 Logical Nodes):
  1. ESP32 Development Board
  2. MPU9250 9-Axis IMU (Acc X/Y/Z, Gyro X/Y/Z, Mag X/Y/Z, derived tilt)
  3. BME280 (Temperature, Humidity, Barometric Pressure)
  4. Draw-wire / String Displacement Sensor
  5. Mechanical Crack-Opening Gauge + Potentiometric Sensor (Crack Width mm)
  6. ADS1115 16-bit ADC (Configurable channel mapping: A0=Displacement, A1=Crack)
  7. DS3231 Precision I2C RTC (Hardware offline timestamping)
  8. microSD Card Module (Local node offline backup)
  9. SX1276/SX1278 LoRa Module — IN865 / India Variant (865-867 MHz)
  10. 865 MHz matching LoRa antenna
  11. Solar Panel + 1S LiFePO4 Battery + LiFePO4 Charging & Protection Circuit
  12. IP65/IP67 Enclosure + Cable Glands & Mounting Hardware
- CENTRAL GATEWAY ×1:
  1. Raspberry Pi Zero 2 W
  2. IN865 LoRa Gateway Module (865 MHz)
  3. 865 MHz LoRa Antenna
  4. SIM7600E-H 4G LTE USB Development Board + 4G LTE Antenna
  5. microSD Card (Local gateway buffering)
  6. 5V / 3A Power Supply
  7. Warning Buzzer + Strobe Warning LED
=============================================================================
"""

import os

# MQTT Broker Settings
MQTT_BROKER_HOST = os.getenv("MQTT_BROKER_HOST", "localhost")
MQTT_BROKER_PORT = int(os.getenv("MQTT_BROKER_PORT", 1883))
MQTT_USERNAME = os.getenv("MQTT_USERNAME", "")
MQTT_PASSWORD = os.getenv("MQTT_PASSWORD", "")
MQTT_KEEPALIVE = 60

# MINEGATE Gateway ID
GATEWAY_ID = os.getenv("GATEWAY_ID", "MINEGATE-01")

# MINEGATE MQTT Topic Hierarchy
TOPIC_GATEWAY_TELEMETRY = f"minegate/{GATEWAY_ID}/telemetry"
TOPIC_GATEWAY_ALERTS = f"minegate/{GATEWAY_ID}/alerts"
TOPIC_GATEWAY_STATUS = f"minegate/{GATEWAY_ID}/status"
TOPIC_GATEWAY_COMMANDS = f"minegate/{GATEWAY_ID}/commands"
TOPIC_GATEWAY_SYNC = f"minegate/{GATEWAY_ID}/sync"

# Physical Mine Geometry: Panel A (Surface Strata Grid)
# Base Anchor: Jharia Coalfield, Jharkhand (Lat: 23.7500° N, Lon: 86.4200° E)
BASE_LAT = 23.7500
BASE_LON = 86.4200
METERS_PER_DEG_LAT = 111320.0
METERS_PER_DEG_LON = 40075000.0 * 0.9153 / 360.0  # cos(23.75 deg) ~ 0.9153

def local_xy_to_latlon(x_m: float, y_m: float):
    lat = BASE_LAT + (y_m / METERS_PER_DEG_LAT)
    lon = BASE_LON + (x_m / METERS_PER_DEG_LON)
    return round(lat, 7), round(lon, 7)

# Central Gateway (MINEGATE Surface Master Station on Raspberry Pi Zero 2 W)
GATEWAY_NODE = {
    "gateway_id": GATEWAY_ID,
    "name": "MINEGATE Surface Central Gateway",
    "hardware": "Raspberry Pi Zero 2 W + IN865 LoRa HAT + SIM7600E-H 4G LTE",
    "lat": BASE_LAT,
    "lon": BASE_LON,
    "status": "ONLINE"
}

# Dynamic Multi-Hop Mesh Routes for 20 Nodes
# Supports Direct (NODE -> GATEWAY) and Multi-Hop (NODE_04 -> NODE_03 -> NODE_01 -> GATEWAY)
DYNAMIC_ROUTES = {
    "NODE_01": {"parent": None, "hop": 1, "route": ["NODE_01"]},
    "NODE_02": {"parent": None, "hop": 1, "route": ["NODE_02"]},
    "NODE_03": {"parent": "NODE_01", "hop": 2, "route": ["NODE_03", "NODE_01"]},
    "NODE_04": {"parent": "NODE_03", "hop": 3, "route": ["NODE_04", "NODE_03", "NODE_01"]},
    "NODE_05": {"parent": "NODE_04", "hop": 4, "route": ["NODE_05", "NODE_04", "NODE_03", "NODE_01"]},
    "NODE_06": {"parent": None, "hop": 1, "route": ["NODE_06"]},
    "NODE_07": {"parent": "NODE_06", "hop": 2, "route": ["NODE_07", "NODE_06"]},
    "NODE_08": {"parent": "NODE_07", "hop": 3, "route": ["NODE_08", "NODE_07", "NODE_06"]},
    "NODE_09": {"parent": "NODE_08", "hop": 4, "route": ["NODE_09", "NODE_08", "NODE_07", "NODE_06"]},
    "NODE_10": {"parent": "NODE_02", "hop": 2, "route": ["NODE_10", "NODE_02"]},
    "NODE_11": {"parent": None, "hop": 1, "route": ["NODE_11"]},
    "NODE_12": {"parent": "NODE_11", "hop": 2, "route": ["NODE_12", "NODE_11"]},
    "NODE_13": {"parent": "NODE_12", "hop": 3, "route": ["NODE_13", "NODE_12", "NODE_11"]},
    "NODE_14": {"parent": "NODE_13", "hop": 4, "route": ["NODE_14", "NODE_13", "NODE_12", "NODE_11"]},
    "NODE_15": {"parent": "NODE_10", "hop": 3, "route": ["NODE_15", "NODE_10", "NODE_02"]},
    "NODE_16": {"parent": None, "hop": 1, "route": ["NODE_16"]},
    "NODE_17": {"parent": "NODE_16", "hop": 2, "route": ["NODE_17", "NODE_16"]},
    "NODE_18": {"parent": "NODE_17", "hop": 3, "route": ["NODE_18", "NODE_17", "NODE_16"]},
    "NODE_19": {"parent": "NODE_18", "hop": 4, "route": ["NODE_19", "NODE_18", "NODE_17", "NODE_16"]},
    "NODE_20": {"parent": "NODE_15", "hop": 4, "route": ["NODE_20", "NODE_15", "NODE_10", "NODE_02"]}
}

# 20 MINEGUARD Surface Sensor Nodes in Panel A Grid (4 rows x 5 columns)
NODES_CONFIG = {}
for i in range(1, 21):
    node_code = f"NODE_{i:02d}"
    row = (i - 1) // 5
    col = (i - 1) % 5

    x_m = float((col + 1) * 35.0)
    y_m = float((row + 1) * 35.0)
    lat, lon = local_xy_to_latlon(x_m, y_m)
    route_info = DYNAMIC_ROUTES.get(node_code, {"parent": None, "hop": 1, "route": [node_code]})

    NODES_CONFIG[node_code] = {
        "node_id": node_code,
        "node_code": node_code,
        "device_id": f"ESP32-MG-{i:03d}",
        "panel": "Panel-A-North",
        "grid_index": i,
        "row": row,
        "col": col,
        "lat": lat,
        "lon": lon,
        "hardware": {
            "mcu": "ESP32 DevKit V1",
            "imu": "MPU9250 9-Axis (Acc/Gyro/Mag/Tilt)",
            "environment": "BME280 (Temperature, Humidity, Barometric Pressure)",
            "displacement": "Draw-Wire / String Potentiometer (ADS1115 A0)",
            "crack_sensor": "Mechanical Crack-Opening Potentiometric Gauge (ADS1115 A1)",
            "adc": "ADS1115 16-Bit I2C ADC (Configurable A0-A3 Mapping)",
            "rtc": "DS3231 Precision I2C RTC",
            "lora_module": "SX1276/SX1278 IN865 (865.2 MHz / 865.5 MHz / 865.8 MHz)",
            "antenna": "865 MHz Matched LoRa Antenna",
            "power": "1S LiFePO4 3.2V 3200mAh + Solar Harvester + Protection Circuit",
            "local_storage": "microSD Card Offline Buffer",
            "enclosure": "IP67 Weatherproof Industrial Enclosure + Cable Glands"
        },
        "baseline": {
            # MPU9250 Motion
            "tilt_x_deg": 0.05,
            "tilt_y_deg": 0.02,
            "accel_x_g": 0.002,
            "accel_y_g": 0.001,
            "accel_z_g": 1.000,
            "gyro_x_dps": 0.01,
            "gyro_y_dps": 0.01,
            "gyro_z_dps": 0.00,
            "mag_x_ut": 22.5,
            "mag_y_ut": -14.2,
            "mag_z_ut": 38.1,
            "vibration_rms_g": 0.025,
            # BME280 Environment
            "temperature_c": 28.5,
            "humidity_pct": 55.0,
            "pressure_hpa": 1013.25,
            # Displacement & Crack
            "displacement_mm": 1.2,
            "displacement_rate_mm_hr": 0.02,
            "displacement_baseline_mm": 1.0,
            "crack_width_mm": 0.0,
            "crack_detected": False,
            # Power
            "battery_pct": 98.0 - (i * 0.3),
            "battery_voltage_v": 3.32
        },
        "rf": {
            "frequency_mhz": 865.2 if i % 3 == 0 else (865.5 if i % 3 == 1 else 865.8),
            "spreading_factor": 7 if route_info["hop"] <= 2 else 8,
            "bandwidth_khz": 125.0,
            "rssi_dbm": -68 - (route_info["hop"] * 10),
            "snr_db": 10.0 - (route_info["hop"] * 1.2),
            "hop_count": route_info["hop"],
            "parent_node_id": route_info["parent"],
            "mesh_route": route_info["route"]
        }
    }

SAMPLING_INTERVAL_SECONDS = 3.0
HEARTBEAT_INTERVAL_SECONDS = 15.0

MQTT_CONFIG = {
    "host": MQTT_BROKER_HOST,
    "port": MQTT_BROKER_PORT,
    "interval": SAMPLING_INTERVAL_SECONDS
}

# MINEGUARD — System Architecture Specification
## SIH26025 — Geotechnical Mine Subsidence Monitoring System

---

## 1. System Topology Overview

```
 [ SENSOR NODE ×4 Physical (20 Logical) ]
   ├── ESP32 Microcontroller
   ├── MPU9250 9-Axis IMU (Acc, Gyro, Mag, Tilt)
   ├── BME280 (Temp, Humidity, Pressure)
   ├── Draw-Wire / String Potentiometer (Displacement, Rate)
   ├── Mechanical Crack Gauge + Potentiometer (Crack Width)
   ├── ADS1115 16-bit ADC (A0: Disp, A1: Crack)
   ├── DS3231 Precision RTC (Offline Timestamps)
   ├── microSD Local Buffer (Node Offline Storage)
   └── SX1276/SX1278 IN865 LoRa Module (865 MHz)
                    │
                    ▼  (Sub-GHz IN865 Dynamic LoRa Mesh)
 [ MINEGATE CENTRAL GATEWAY ×1 ]
   ├── Raspberry Pi Zero 2 W
   ├── IN865 LoRa Gateway Concentrator
   ├── SIM7600E-H 4G LTE Backhaul (Optional / Sync only)
   ├── microSD Edge Buffer (SQLite Local Storage)
   ├── Industrial Siren & Alarm Relay (GPIO 18)
   └── Mosquitto MQTT Broker (port 1883)
                    │
                    ▼  (Edge & Local LAN)
 [ BACKEND SERVICES ]
   ├── FastAPI High-Performance Async Framework
   ├── PostgreSQL 18 Primary Database (`mine_monitoring`)
   ├── PostGIS Spatial Engine (ST_Distance, ST_SetSRID, GeoJSON)
   ├── Multi-Factor Geotechnical AI / ML Pipeline
   └── WebSocket Live Telemetry / Alerts Broadcaster
                    │
                    ▼
 [ MINEGUARD PWA DASHBOARD ]
   ├── React 18 + Vite + Tailwind CSS
   ├── Live 9-Axis Motion, BME280 & Displacement Cards
   ├── PostGIS Interactive Strata GIS Map (Leaflet)
   ├── LoRa Mesh Topology Graph
   └── Node Physical Locator (Buzzer/LED Downlink Trigger)
```

---

## 2. Core Safety Guarantees (Offline-First, Mesh-First, Edge-First)

1. **Zero Internet Requirement for Safety**:
   - Geotechnical sampling, continuous displacement monitoring, crack opening measurement, 9-axis motion detection, LoRa mesh routing, local ML anomaly evaluation, siren actuation, and physical node location **function 100% locally without cloud or Internet connectivity**.
2. **Dual-Layer Offline Persistence**:
   - **Layer 1 (Node Level)**: microSD card on each ESP32 saves readings locally when LoRa radio is blocked.
   - **Layer 2 (Gateway Level)**: microSD SQLite buffer on the Raspberry Pi Zero 2 W queues data when PostgreSQL or network is restarting.
3. **Multi-Hop LoRa Mesh**:
   - Dynamic packet forwarding across sensor nodes ensuring deep-quadrant coverage even without line-of-sight to the surface gateway.

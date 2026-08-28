# MINEGUARD — AI-Enabled Real-Time Mine Subsidence Monitoring & Early Warning System
## Problem Statement: SIH26025 | Team: RED HACK

---

### Executive Overview
**MINEGUARD** is an offline-first geotechnical monitoring platform designed to detect surface strata deformation, ground subsidence, tension cracks, and micro-seismic vibrations across open-pit and underground mining panels.

The system integrates:
- **20 MINEGUARD Sensor Nodes**: Powered by ESP32 DevKit V1 microcontrollers with dual IMUs (MPU6050 & ADXL345), BME280 environmental sensing, ADS1115 16-bit ADC connected to Draw-Wire displacement and DIY crack-opening gauges, DS3231 RTC, local MicroSD logging, and SX1276/SX1278 LoRa transceivers powered by solar LiFePO4 battery systems.
- **MINEGATE Central Edge Gateway**: Raspberry Pi Zero 2 W with an SX1302/SX1303 8-Channel LoRa Concentrator HAT, local Mosquitto MQTT broker, SQLite zero-loss buffering database, GPIO 18 siren relay controller, and local FastAPI backend.
- **Edge AI / ML Anomaly Detection**: Local Isolation Forest anomaly detector trained on multivariate geotechnical features (tilt rate, displacement velocity, vibration RMS, crack state) generating a 0–100 Risk Score.
- **Offline-First PWA Dashboard**: High-contrast, bright-themed React 18 PWA with PostGIS spatial maps, real-time WebSocket telemetry, bidirectional LoRa "Find My Node" locator (Buzzer + Strobe LED), and automatic cloud synchronization on reconnection.

---

### Core Communication Architecture
```
[ MINEGUARD ESP32 Sensor Nodes (1..20) ]
                  │
                  ▼ (SX1276 / SX1278 LoRa RF @ 868 MHz)
        [ LoRa Field Network ]
                  │
                  ▼ (SX1302 / SX1303 8-Channel LoRa Concentrator)
[ MINEGATE Central Gateway (Raspberry Pi Zero 2 W) ]
   ├── Local Mosquitto MQTT Broker
   ├── Local SQLite Zero-Loss Buffer (edge_buffer.db)
   ├── Local GPIO Pin 18 Siren / Warning Light Relay
   ├── Local Isolation Forest Machine Learning Inference
   └── Local FastAPI Backend Service & WebSockets
                  │
                  ▼ (Local Wi-Fi AP / Network)
       [ Local React PWA Dashboard ]
                  │
                  ▼ (When 4G / WAN Internet is Available)
[ Cloud Synchronization: PostgreSQL + PostGIS & SMS/Email Alerts ]
```

---

### Key System Capabilities
1. **100% Offline Field Autonomy**: No internet required for core sensing, LoRa packet reception, risk scoring, local siren triggering, or operator dashboard display.
2. **Node-Agnostic Architecture**: Any node from `NODE_01` to `NODE_20` can experience movement, trigger critical alarms, or be located on demand.
3. **Hardware Abstraction Layer**: `FieldTransportAdapter` seamlessly unifies physical SX1302 LoRa hardware and the 20-node software simulator.
4. **Bidirectional Hardware Locator**: Operators can trigger an acoustic buzzer and ultra-bright strobe LED on any registered node over LoRa downlink.
5. **Safe Database Relational Model**: Uses `SERIAL` / `INTEGER` primary and foreign keys matching existing PostgreSQL tables (`panels`, `nodes`, `sensor_readings`).

# MINEGUARD — Final Hardware Integration & Pinout Specification
## SIH26025 — Geotechnical Mine Subsidence Monitoring System

---

## 1. MINEGUARD Sensor Node Architecture (×4 Physical Prototype / 20 Logical Grid)

Each physical MINEGUARD sensor station is deployed in an **IP65/IP67 weatherproof industrial enclosure** with cable glands, conduit, and mounting brackets:

| # | Component | Interface / Pins | Function |
|---|---|---|---|
| 1 | **ESP32 DevKit V1** | Master Microcontroller | Main compute, sampling, mesh protocol & power management |
| 2 | **MPU9250 9-Axis IMU** | I2C (`SDA`: GPIO 21, `SCL`: GPIO 22, Addr: `0x68`) | 3-Axis Accel + 3-Axis Gyro + 3-Axis Magnetometer + Strata Tilt |
| 3 | **BME280** | I2C (`SDA`: GPIO 21, `SCL`: GPIO 22, Addr: `0x76`) | Surface temperature, relative humidity, barometric pressure |
| 4 | **Draw-Wire / String Potentiometer** | Analog via ADS1115 (`Channel A0`) | Continuous geotechnical ground displacement & displacement rate |
| 5 | **Mechanical Crack-Opening Gauge + Potentiometer** | Analog via ADS1115 (`Channel A1`) | Fissure / crack-width measurement (0–10 mm range) |
| 6 | **ADS1115 16-Bit I2C ADC** | I2C (`SDA`: GPIO 21, `SCL`: GPIO 22, Addr: `0x48`) | High-resolution analog acquisition with configurable channel mapping |
| 7 | **DS3231 Precision RTC** | I2C (`SDA`: GPIO 21, `SCL`: GPIO 22, Addr: `0x68`) | Hardware real-time clock timestamping when offline/disconnected |
| 8 | **microSD Card Module** | SPI (`SCK`: 18, `MISO`: 19, `MOSI`: 23, `CS`: 15) | Local node-side emergency data buffer during communication loss |
| 9 | **SX1276/SX1278 LoRa Module** | SPI (`NSS`: 5, `RST`: 14, `DIO0`: 26, `SCK`: 18, `MISO`: 19, `MOSI`: 23) | IN865 LoRa India Variant (865.2 MHz / 865.5 MHz / 865.8 MHz) |
| 10 | **865 MHz LoRa Antenna** | SMA / u.FL | Matched Sub-GHz high-gain antenna |
| 11 | **Solar Panel & Harvester** | 5V / 1A Solar Input | Continuous energy harvesting |
| 12 | **1S LiFePO4 Battery** | 3.2V Nominal (3200 mAh) | High-thermal-stability safe mining battery |
| 13 | **LiFePO4 Charging & Protection** | TP5000 / BMS Circuit | Overcharge, over-discharge, and short-circuit protection |
| 14 | **Piezo Buzzer** | GPIO 4 (PWM Output) | Acoustic emergency evacuation and hardware locator signal |
| 15 | **Strobe Warning LED** | GPIO 2 (Digital Output) | High-brightness visual beacon for node physical location |

---

## 2. MINEGATE Central Gateway Architecture (×1 Surface Master Station)

| # | Component | Interface | Function |
|---|---|---|---|
| 1 | **Raspberry Pi Zero 2 W** | Central Processing Unit | Local edge broker, local SQLite fallback buffer, siren relay controller |
| 2 | **IN865 LoRa Gateway Module** | SPI / GPIO | 865 MHz LoRa packet concentrator receiving all multi-hop packets |
| 3 | **865 MHz LoRa Antenna** | SMA connector | Surface omnidirectional LoRa antenna |
| 4 | **SIM7600E-H 4G LTE USB Board** | USB / UART | Cellular WAN backhaul for remote cloud synchronization (when available) |
| 5 | **4G LTE Antenna** | SMA connector | Cellular external antenna |
| 6 | **microSD Card** | SDIO | Edge database buffer, logging, and operating system |
| 7 | **5V / 3A Power Supply** | Micro-USB | Gateway surface main power |
| 8 | **Industrial Siren & Buzzer** | GPIO 18 Relay Actuation | Evacuation acoustic siren for critical subsidence alerts |
| 9 | **Warning LED Beacon** | GPIO 17 Relay Actuation | Visual emergency indicator |

---

## 3. IN865 Dynamic Mesh Routing Topology

Communication operates on the **IN865 (865–867 MHz)** Indian license-free ISM band with dynamic multi-hop routing:

```
[ NODE_05 ] 
    │  (Hop 4)
    ▼
[ NODE_04 ] 
    │  (Hop 3)
    ▼
[ NODE_03 ] 
    │  (Hop 2)
    ▼
[ NODE_01 ] ────► [ MINEGATE Gateway (RPi Zero 2 W) ] ────► [ FastAPI + PostgreSQL + PostGIS ]
(Hop 1 Direct)
```

Direct connections and multi-hop paths are dynamically selected based on signal strength (RSSI), SNR, and link availability.

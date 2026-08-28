# MINEGUARD SENSOR NODE & MINEGATE HARDWARE ARCHITECTURE
## SIH26025 — Physical Geotechnical Telemetry Node

### 1. MINEGUARD Sensor Node Overview
- **MCU**: ESP32 DevKit V1 (240 MHz Dual-Core Xtensa LX6)
- **Tilt & Orientation**: MPU6050 6-DOF IMU (I2C: `0x68`)
- **Vibration & Shock**: ADXL345 3-Axis Digital Accelerometer (I2C: `0x53`)
- **Environment**: BME280 Temperature, Humidity & Pressure (I2C: `0x76`)
- **Displacement**: String Potentiometer / Draw-Wire Sensor (connected to ADS1115 Channel `A0`)
- **Crack Detection**: DIY Crack-Opening Fissure Gauge (connected to ADS1115 Channel `A1`)
- **ADC**: ADS1115 16-Bit Ultra-Precision ADC (I2C: `0x48`)
- **RTC**: DS3231 Precision Hardware Real-Time Clock with battery backup (I2C: `0x68`)
- **LoRa Transceiver**: Semtech SX1276 / SX1278 (SPI interface, 868 MHz / 915 MHz)
- **Power System**: 3.2V LiFePO4 Battery + Solar Charge Controller + INA219 Power Monitor (I2C: `0x40`)
- **Local Storage**: MicroSD SPI Module (Local edge backup)
- **Local Alarm & Locator**: Active Piezo Buzzer (`GPIO 4`) + High-Brightness Strobe LED (`GPIO 2`)
- **Enclosure**: IP67 Weatherproof Surface Mount Box

---

### 2. Complete ESP32 DevKit V1 Pinout Table

| Component | Interface / Pins | ESP32 GPIO | Description |
|-----------|------------------|------------|-------------|
| **I2C Bus** | `SDA` | `GPIO 21` | Shared I2C Data (MPU6050, ADXL345, BME280, ADS1115, INA219, DS3231) |
| **I2C Bus** | `SCL` | `GPIO 22` | Shared I2C Clock (100kHz / 400kHz) |
| **SX1276 LoRa** | `SCK` | `GPIO 18` | SPI Clock |
| **SX1276 LoRa** | `MISO` | `GPIO 19` | SPI Master In Slave Out |
| **SX1276 LoRa** | `MOSI` | `GPIO 23` | SPI Master Out Slave In |
| **SX1276 LoRa** | `NSS / CS` | `GPIO 5` | SPI Chip Select |
| **SX1276 LoRa** | `RST` | `GPIO 14` | Hardware Reset |
| **SX1276 LoRa** | `DIO0` | `GPIO 26` | TX/RX Done Interrupt |
| **ADS1115** | `A0` | — | Draw-Wire Displacement Potentiometer Signal (0–3.3V) |
| **ADS1115** | `A1` | — | DIY Crack Gauge Break-Wire / Resistive Shift Signal |
| **Buzzer** | `SIG` | `GPIO 4` | Active Buzzer Driver (Transistor base / Gate) |
| **Strobe LED** | `ANODE` | `GPIO 2` | High-Visibility Locator Indicator |
| **MicroSD** | `CS` | `GPIO 15` | MicroSD SPI Chip Select |

---

### 3. Central Gateway — MINEGATE Overview
- **Processor**: Raspberry Pi Zero 2 W (Quad-Core 64-bit ARM Cortex-A53 @ 1.0 GHz)
- **LoRa Concentrator**: SX1302 / SX1303 8-Channel Multi-Spreading-Factor Concentrator Hat (SPI)
- **Cellular Backup**: 4G LTE HAT (SIM7600 / Quectel EC25)
- **Local Alarm Interface**: Relay connected to `GPIO 18` for 110dB Industrial Siren & Beacon
- **Local Storage**: MicroSD Class 10 with SQLite `edge_buffer.db` (Zero data loss offline guarantee)
- **Local Network**: Local Wi-Fi Access Point + Mosquitto MQTT + FastAPI + PWA Host

---

### 4. Flashing Firmware via PlatformIO
```bash
cd firmware/esp32_node
pio run --target upload
```

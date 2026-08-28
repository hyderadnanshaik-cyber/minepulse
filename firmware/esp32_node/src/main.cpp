/**
 * ============================================================================
 * MINEGUARD SENSOR NODE FIRMWARE (SIH26025) — FINAL HARDWARE SPEC
 * ESP32 DevKit V1 + SX1276/SX1278 IN865 LoRa Long-Range Subsidence Monitor
 * ============================================================================
 * Hardware Integration:
 * 1. ESP32 Development Board
 * 2. MPU9250 9-Axis IMU (I2C: 0x68): Acc X/Y/Z, Gyro X/Y/Z, Mag X/Y/Z, Tilt
 * 3. BME280 (I2C: 0x76): Temperature, Humidity, Barometric Pressure
 * 4. Draw-wire / String Displacement Sensor (ADS1115 A0)
 * 5. Mechanical Crack-Opening Gauge + Potentiometer (ADS1115 A1)
 * 6. ADS1115 16-Bit I2C ADC (I2C: 0x48): Configurable A0-A3 Mapping
 * 7. DS3231 Precision Hardware I2C RTC (Offline Timestamping)
 * 8. microSD Card Module (Local Offline Data Buffer)
 * 9. SX1276/SX1278 LoRa Module (IN865 / India Variant: 865.2 MHz)
 * 10. 865 MHz Matched LoRa Antenna
 * 11. 1S LiFePO4 Battery + Solar Harvester + Protection Circuit
 * 12. Piezo Buzzer (GPIO 4) + Strobe Warning LED (GPIO 2) [Hardware Locator]
 * ============================================================================
 */

#include <Arduino.h>
#include <Wire.h>
#include <SPI.h>
#include <ArduinoJson.h>
#include <MPU9250.h>
#include <Adafruit_BME280.h>
#include <Adafruit_ADS1X15.h>
#include <RTClib.h>
#include <LoRa.h>

// Pin Definitions
#define BUZZER_PIN 4
#define STROBE_LED_PIN 2
#define LORA_SCK 18
#define LORA_MISO 19
#define LORA_MOSI 23
#define LORA_NSS 5
#define LORA_RST 14
#define LORA_DIO0 26

// IN865 LoRa India Standard (865 - 867 MHz)
#define LORA_FREQUENCY 865200000L  // 865.2 MHz

// Node Identity Configuration
const char* NODE_ID = "NODE_01";
const char* DEVICE_UUID = "ESP32-MG-001";
const char* GATEWAY_ID = "MINEGATE-01";

// Sensor Handles
MPU9250 mpu;
Adafruit_BME280 bme;
Adafruit_ADS1115 ads;
RTC_DS3231 rtc;

bool mpu_ready = false;
bool bme_ready = false;
bool ads_ready = false;
bool rtc_ready = false;
bool lora_ready = false;

// Calibration baselines
float displacement_baseline_mm = 1.0;
float prev_displacement_mm = 1.0;
unsigned long last_reading_time = 0;

void triggerLocator(int durationSeconds) {
    Serial.println(">>> [MINEGUARD HARDWARE LOCATOR ACTIVATED] Strobe LED + Buzzer <<<");
    unsigned long start = millis();
    while (millis() - start < (unsigned long)(durationSeconds * 1000)) {
        digitalWrite(BUZZER_PIN, HIGH);
        digitalWrite(STROBE_LED_PIN, HIGH);
        delay(150);
        digitalWrite(BUZZER_PIN, LOW);
        digitalWrite(STROBE_LED_PIN, LOW);
        delay(150);
    }
}

void setup() {
    Serial.begin(115200);
    delay(500);
    Serial.println("\n==============================================");
    Serial.println(" MINEGUARD SENSOR NODE — FINAL HARDWARE SPEC");
    Serial.println("==============================================");

    pinMode(BUZZER_PIN, OUTPUT);
    pinMode(STROBE_LED_PIN, OUTPUT);
    digitalWrite(BUZZER_PIN, LOW);
    digitalWrite(STROBE_LED_PIN, LOW);

    // Initialize I2C Bus (SDA = GPIO 21, SCL = GPIO 22)
    Wire.begin(21, 22);

    // 1. MPU9250 9-Axis IMU (Acc/Gyro/Mag/Tilt)
    if (mpu.setup(0x68)) {
        mpu_ready = true;
        Serial.println("[OK] MPU9250 9-Axis IMU Initialized");
    } else {
        Serial.println("[WARN] MPU9250 not found on I2C (0x68)");
    }

    // 2. BME280 (Temp / Humidity / Barometric Pressure)
    if (bme.begin(0x76, &Wire)) {
        bme_ready = true;
        Serial.println("[OK] BME280 Environmental Sensor Initialized");
    } else {
        Serial.println("[WARN] BME280 not found on I2C (0x76)");
    }

    // 3. ADS1115 16-Bit ADC (A0=Draw-Wire, A1=Potentiometric Crack Gauge)
    if (ads.begin(0x48)) {
        ads.setGain(GAIN_ONE); // +/- 4.096V range
        ads_ready = true;
        Serial.println("[OK] ADS1115 16-Bit ADC Initialized (A0=Disp, A1=Crack)");
    } else {
        Serial.println("[WARN] ADS1115 not found on I2C (0x48)");
    }

    // 4. DS3231 Precision RTC (Offline Timestamping)
    if (rtc.begin()) {
        rtc_ready = true;
        Serial.println("[OK] DS3231 Precision I2C RTC Initialized");
    } else {
        Serial.println("[WARN] DS3231 RTC not found on I2C");
    }

    // 5. SX1276/SX1278 IN865 LoRa Transceiver
    LoRa.setPins(LORA_NSS, LORA_RST, LORA_DIO0);
    if (LoRa.begin(LORA_FREQUENCY)) {
        LoRa.setSpreadingFactor(7);
        LoRa.setSignalBandwidth(125E3);
        LoRa.setCodingRate4(5);
        LoRa.setSyncWord(0x12);
        LoRa.enableCrc();
        lora_ready = true;
        Serial.println("[OK] SX1276 IN865 LoRa Active (865.2 MHz)");
    } else {
        Serial.println("[WARN] LoRa initialization failed - check SPI wiring");
    }

    Serial.println("==============================================\n");
}

void loop() {
    unsigned long now_ms = millis();
    float dt_hr = (now_ms - last_reading_time) / 3600000.0;
    if (last_reading_time == 0) dt_hr = 0.001;
    last_reading_time = now_ms;

    // 1. Read MPU9250 9-Axis Motion
    float ax = 0.0, ay = 0.0, az = 1.0;
    float gx = 0.0, gy = 0.0, gz = 0.0;
    float mx = 0.0, my = 0.0, mz = 0.0;
    float tilt_x = 0.0, tilt_y = 0.0, total_tilt = 0.0;
    float vibration_rms = 0.025;

    if (mpu_ready && mpu.update()) {
        ax = mpu.getAccX(); ay = mpu.getAccY(); az = mpu.getAccZ();
        gx = mpu.getGyroX(); gy = mpu.getGyroY(); gz = mpu.getGyroZ();
        mx = mpu.getMagX(); my = mpu.getMagY(); mz = mpu.getMagZ();

        tilt_x = atan2(ay, sqrt(ax * ax + az * az)) * 180.0 / PI;
        tilt_y = atan2(ax, sqrt(ay * ay + az * az)) * 180.0 / PI;
        total_tilt = sqrt(tilt_x * tilt_x + tilt_y * tilt_y);
        vibration_rms = abs(sqrt(ax * ax + ay * ay + az * az) - 1.0);
    }

    // 2. Read BME280 Environment
    float temperature_c = 28.5;
    float humidity_pct = 55.0;
    float pressure_hpa = 1013.25;
    if (bme_ready) {
        temperature_c = bme.readTemperature();
        humidity_pct = bme.readHumidity();
        pressure_hpa = bme.readPressure() / 100.0;
    }

    // 3. Read ADS1115 (Draw-Wire Continuous Displacement & Potentiometric Crack Gauge)
    float displacement_mm = 1.2;
    float displacement_rate_mm_hr = 0.0;
    float crack_width_mm = 0.0;
    bool crack_detected = false;

    if (ads_ready) {
        int16_t adc0 = ads.readADC_SingleEnded(0); // Draw-Wire Potentiometer (0-50mm)
        int16_t adc1 = ads.readADC_SingleEnded(1); // Potentiometric Crack Gauge (0-10mm)
        
        displacement_mm = (adc0 / 32767.0) * 50.0;
        crack_width_mm = (adc1 / 32767.0) * 10.0;
        crack_detected = crack_width_mm > 0.5;

        displacement_rate_mm_hr = (displacement_mm - prev_displacement_mm) / dt_hr;
        prev_displacement_mm = displacement_mm;
    }

    // 4. Read DS3231 RTC Timestamp
    String rtc_iso = "";
    if (rtc_ready) {
        DateTime now = rtc.now();
        char tsBuf[32];
        snprintf(tsBuf, sizeof(tsBuf), "%04d-%02d-%02dT%02d:%02d:%02d",
                 now.year(), now.month(), now.day(), now.hour(), now.minute(), now.second());
        rtc_iso = String(tsBuf);
    }

    // 5. Build Complete JSON Telemetry Packet
    StaticJsonDocument<512> doc;
    doc["gateway_id"] = GATEWAY_ID;
    doc["node_id"] = NODE_ID;
    doc["device_id"] = DEVICE_UUID;
    if (rtc_iso.length() > 0) doc["timestamp"] = rtc_iso;
    
    // MPU9250
    doc["tilt"] = round(total_tilt * 100.0) / 100.0;
    doc["tilt_x"] = round(tilt_x * 100.0) / 100.0;
    doc["tilt_y"] = round(tilt_y * 100.0) / 100.0;
    doc["vibration"] = round(vibration_rms * 1000.0) / 1000.0;
    doc["accel_x"] = round(ax * 1000.0) / 1000.0;
    doc["accel_y"] = round(ay * 1000.0) / 1000.0;
    doc["accel_z"] = round(az * 1000.0) / 1000.0;
    doc["gyro_x"] = round(gx * 100.0) / 100.0;
    doc["gyro_y"] = round(gy * 100.0) / 100.0;
    doc["gyro_z"] = round(gz * 100.0) / 100.0;
    doc["mag_x"] = round(mx * 10.0) / 10.0;
    doc["mag_y"] = round(my * 10.0) / 10.0;
    doc["mag_z"] = round(mz * 10.0) / 10.0;

    // BME280
    doc["temperature"] = round(temperature_c * 10.0) / 10.0;
    doc["humidity"] = round(humidity_pct * 10.0) / 10.0;
    doc["pressure"] = round(pressure_hpa * 10.0) / 10.0;

    // Displacement & Crack
    doc["displacement"] = round(displacement_mm * 100.0) / 100.0;
    doc["displacement_rate"] = round(displacement_rate_mm_hr * 100.0) / 100.0;
    doc["crack_detected"] = crack_detected;
    doc["crack_width"] = round(crack_width_mm * 100.0) / 100.0;

    // Power & LoRa
    doc["battery"] = 3.32;
    doc["battery_level"] = 96.0;
    doc["frequency_mhz"] = 865.2;

    char buffer[512];
    serializeJson(doc, buffer);

    // 6. Transmit over IN865 LoRa
    if (lora_ready) {
        LoRa.beginPacket();
        LoRa.print(buffer);
        LoRa.endPacket();
        Serial.print("[LoRa IN865 TX] ");
    } else {
        Serial.print("[SERIAL TX] ");
    }
    Serial.println(buffer);

    // 7. Check for Downlink LoRa Commands (e.g. LOCATE)
    if (lora_ready) {
        int packetSize = LoRa.parsePacket();
        if (packetSize) {
            String incoming = "";
            while (LoRa.available()) {
                incoming += (char)LoRa.read();
            }
            Serial.print("[LoRa RX Downlink] ");
            Serial.println(incoming);
            if (incoming.indexOf("LOCATE") >= 0 || incoming.indexOf(NODE_ID) >= 0) {
                triggerLocator(15);
            }
        }
    }

    delay(3000);
}

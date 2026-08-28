import time
import json
import random
import logging
from typing import Dict, List
import paho.mqtt.client as mqtt
from simulator.config import (
    NODES_CONFIG,
    GATEWAY_ID,
    TOPIC_GATEWAY_TELEMETRY,
    TOPIC_GATEWAY_COMMANDS,
    TOPIC_GATEWAY_ALERTS,
    MQTT_CONFIG
)
from simulator.scenarios import ScenarioManager

logging.basicConfig(level=logging.INFO, format="%(asctime)s [MINEGUARD-SIM] %(message)s")
logger = logging.getLogger("NodeSimulator")

class NodeSimulator:
    """
    20-Node LoRa Sensor Network Simulator for MINEGUARD — FINAL HARDWARE SPEC.
    Simulates:
    - 20 Physical-Grade Sensor Nodes (NODE_01 to NODE_20)
    - Hardware suite:
        1. ESP32 Development Board
        2. MPU9250 9-Axis IMU (Acc X/Y/Z, Gyro X/Y/Z, Mag X/Y/Z, tilt X/Y, vibration)
        3. BME280 (Temperature, Humidity, Pressure)
        4. Draw-wire / String Potentiometer (continuous displacement, rate)
        5. Mechanical Crack-Opening Gauge + Potentiometer (crack width mm)
        6. ADS1115 16-bit ADC (A0=Disp, A1=Crack)
        7. DS3231 Precision I2C RTC (Offline timestamp)
        8. microSD Card Local Backup
        9. SX1276/SX1278 IN865 LoRa Module (865-867 MHz)
        10. 1S LiFePO4 Battery + Solar Harvester
    - Multi-hop LoRa Mesh Routing (e.g. NODE_04 -> NODE_03 -> NODE_01 -> GATEWAY)
    - Downlink command handling (Buzzer + Strobe LED locator for ALL nodes)
    """

    def __init__(self):
        self.nodes_config = NODES_CONFIG
        self.scenario_mgr = ScenarioManager()
        self.client = mqtt.Client(client_id="MINEGUARD-LoRaSim-Daemon")
        self.running = False
        self.gateway_id = GATEWAY_ID

    def on_connect(self, client, userdata, flags, rc):
        logger.info(f"Connected to MQTT Broker (rc={rc})")
        self.client.subscribe(TOPIC_GATEWAY_COMMANDS)
        self.client.subscribe("mine/nodes/+/locate")
        self.client.subscribe("mine/nodes/+/command")
        self.client.subscribe("minegate/+/commands")
        self.client.subscribe("mine/simulator/scenario")
        logger.info(f"Subscribed to MINEGATE downlink commands and simulator scenarios")

    def on_message(self, client, userdata, msg):
        topic = msg.topic
        try:
            payload = json.loads(msg.payload.decode())
        except Exception:
            return

        if topic == "mine/simulator/scenario":
            scen = payload.get("scenario", "ANOMALY_NODE_03")
            self.scenario_mgr.set_mode(scen)
            logger.info(f"🚨 >>> [SCENARIO SWITCHED] Simulator mode changed to: {scen} <<<")
            return

        cmd = payload.get("command") or payload.get("cmd")
        target_node = payload.get("target_node") or payload.get("node_id")

        if not target_node:
            parts = topic.split("/")
            if len(parts) >= 4 and parts[3] == "locate":
                target_node = parts[2]

        if cmd in ["LOCATE", "LOCATE_NODE"] or "locate" in topic:
            duration = payload.get("duration_seconds", payload.get("duration", 15))
            logger.info(
                f"🔔 >>> [MINEGUARD HARDWARE LOCATOR TRIGGERED] Target: {target_node} | "
                f"LoRa SX1276 IN865 Downlink Dispatched -> ESP32 Buzzer (GPIO 4) + Strobe LED (GPIO 2) ACTIVE ({duration}s) <<<"
            )

    def start(self):
        self.running = True
        try:
            self.client.on_connect = self.on_connect
            self.client.on_message = self.on_message
            self.client.connect(MQTT_CONFIG["host"], MQTT_CONFIG["port"], 60)
            self.client.loop_start()
            logger.info("20-Node MINEGUARD LoRa IN865 Field Simulator active. Transmitting telemetry...")
        except Exception as e:
            logger.warning(f"Could not connect to MQTT broker ({e}). Running in standalone output mode.")

        step = 0
        while self.running:
            step += 1
            for node_code, config in self.nodes_config.items():
                mutated = self.scenario_mgr.mutate_telemetry(node_code, config["baseline"], step)
                
                if not mutated.get("is_online", True):
                    continue

                rf = config["rf"]
                # Prepare complete LoRa IN865 field telemetry payload
                reading = {
                    "gateway_id": self.gateway_id,
                    "node_id": node_code,
                    "node_code": node_code,
                    "device_id": config["device_id"],
                    "timestamp": time.time(),
                    # MPU9250 9-Axis Motion
                    "tilt": mutated["total_tilt_deg"],
                    "tilt_x": mutated["tilt_x_deg"],
                    "tilt_y": mutated["tilt_y_deg"],
                    "vibration": mutated["vibration_rms_g"],
                    "accel_x": mutated["accel_x_g"],
                    "accel_y": mutated["accel_y_g"],
                    "accel_z": mutated["accel_z_g"],
                    "gyro_x": mutated["gyro_x_dps"],
                    "gyro_y": mutated["gyro_y_dps"],
                    "gyro_z": mutated["gyro_z_dps"],
                    "mag_x": mutated["mag_x_ut"],
                    "mag_y": mutated["mag_y_ut"],
                    "mag_z": mutated["mag_z_ut"],
                    # BME280 Environment
                    "temperature": mutated["temperature_c"],
                    "humidity": mutated["humidity_pct"],
                    "pressure": mutated["pressure_hpa"],
                    # Draw-Wire Continuous Displacement
                    "displacement": mutated["displacement_mm"],
                    "displacement_rate": mutated["displacement_rate_mm_hr"],
                    "displacement_baseline": mutated["displacement_baseline_mm"],
                    # Potentiometric Mechanical Crack-Opening Gauge
                    "crack_status": bool(mutated["crack_status"]),
                    "crack_detected": bool(mutated["crack_detected"]),
                    "crack_width": mutated["crack_width_mm"],
                    # Power & IN865 LoRa Mesh
                    "battery": mutated["battery_voltage_v"],
                    "battery_level": mutated["battery_pct"],
                    "signal_strength": rf["rssi_dbm"] + random.randint(-2, 2),
                    "rssi": rf["rssi_dbm"] + random.randint(-2, 2),
                    "snr": round(rf["snr_db"] + random.uniform(-0.4, 0.4), 1),
                    "frequency_mhz": rf["frequency_mhz"],
                    "spreading_factor": rf["spreading_factor"],
                    "hop_count": rf["hop_count"],
                    "parent_node_id": rf["parent_node_id"],
                    "route": rf["mesh_route"],
                    "mesh_route": rf["mesh_route"],
                    "latitude": config["lat"],
                    "longitude": config["lon"],
                    "panel": config["panel"],
                    "hardware_spec": "ESP32+MPU9250+BME280+ADS1115+IN865"
                }

                # Publish to MINEGATE concentrator topic
                try:
                    payload_json = json.dumps(reading)
                    self.client.publish(TOPIC_GATEWAY_TELEMETRY, payload_json)
                    self.client.publish(f"mine/nodes/{node_code}/telemetry", payload_json)
                except Exception:
                    pass

            time.sleep(MQTT_CONFIG.get("interval", 3.0))

    def stop(self):
        self.running = False
        try:
            self.client.loop_stop()
            self.client.disconnect()
        except Exception:
            pass

if __name__ == "__main__":
    sim = NodeSimulator()
    try:
        sim.start()
    except KeyboardInterrupt:
        sim.stop()

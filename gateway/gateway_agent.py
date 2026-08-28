import time
import json
import logging
import paho.mqtt.client as mqtt
from gateway.config import GATEWAY_CONFIG
from gateway.local_db import EdgeLocalDB
from gateway.alarm_controller import alarm_controller
from gateway.node_locator import NodeLocatorAdapter
from gateway.sync_service import GatewaySyncService
from gateway.field_transport import SimulatedFieldTransportAdapter

logging.basicConfig(level=logging.INFO, format="%(asctime)s [MINEGATE-EDGE] %(message)s")
logger = logging.getLogger("GatewayAgent")

class GatewayAgent:
    """
    MINEGATE Edge Daemon running on Raspberry Pi Zero 2 W.
    Handles:
    - SX1302/SX1303 LoRa packet intake
    - Local SQLite buffering (zero data loss offline)
    - Local GPIO siren relay actuation (GPIO 18)
    - MQTT translation to backend
    - Background cloud sync daemon upon internet restoration
    """

    def __init__(self):
        self.config = GATEWAY_CONFIG
        self.db = EdgeLocalDB()
        self.sync = GatewaySyncService(self.db)
        self.transport = SimulatedFieldTransportAdapter(node_count=20, gateway_id=self.config["gateway_id"])
        self.mqtt = mqtt.Client(client_id="MINEGATE-Zero2W-Daemon")
        self.locator = NodeLocatorAdapter(self.mqtt, transport=self.transport)

    def on_connect(self, client, userdata, flags, rc):
        logger.info(f"Connected to Mosquitto MQTT Broker with result code {rc}")
        # Subscribe to MINEGATE topics & legacy topics
        gw_id = self.config["gateway_id"]
        self.mqtt.subscribe(f"minegate/{gw_id}/telemetry")
        self.mqtt.subscribe(f"minegate/{gw_id}/alerts")
        self.mqtt.subscribe(f"minegate/{gw_id}/commands")
        self.mqtt.subscribe("mine/nodes/+/telemetry")
        self.mqtt.subscribe("mine/nodes/+/alert")
        self.mqtt.subscribe("mine/gateway/command")
        logger.info(f"MINEGATE Agent subscribed to minegate/{gw_id}/# topics.")

    def on_message(self, client, userdata, msg):
        topic = msg.topic
        try:
            payload = json.loads(msg.payload.decode())
        except Exception:
            return

        parts = topic.split("/")

        # Telemetry intake
        if "telemetry" in topic:
            node_id = payload.get("node_id") or (parts[2] if len(parts) > 2 else "UNKNOWN")
            self.db.insert_telemetry(node_id, payload)

        # Critical alert intake from field nodes
        elif "alert" in topic:
            node_id = payload.get("node_id") or (parts[2] if len(parts) > 2 else "UNKNOWN")
            self.db.insert_alert(node_id, payload)
            if payload.get("severity") == "CRITICAL" or payload.get("risk_score", 0) >= 75:
                logger.warning(f"🚨 CRITICAL ALERT from {node_id} -> Actuating Local GPIO Siren (15s)")
                alarm_controller.activate(15)

        # Gateway commands from PWA / FastAPI
        elif "command" in topic or "commands" in topic:
            cmd = payload.get("command")
            if cmd in ["ACTIVATE_ALARM", "TRIGGER_ALARM"]:
                duration = payload.get("duration", 10)
                alarm_controller.activate(duration)
            elif cmd in ["SILENCE_ALARM", "STOP_ALARM"]:
                alarm_controller.silence()
            elif cmd in ["TEST_ALARM"]:
                alarm_controller.test()
            elif cmd in ["LOCATE_NODE"]:
                target_node = payload.get("target_node") or payload.get("node_id")
                duration = payload.get("duration_seconds", payload.get("duration", 10))
                if target_node:
                    self.locator.locate_node(target_node, duration)

    def start(self):
        self.mqtt.on_connect = self.on_connect
        self.mqtt.on_message = self.on_message
        try:
            self.mqtt.connect(self.config["mqtt_host"], self.config["mqtt_port"], 60)
            self.mqtt.loop_start()
            logger.info("MINEGATE Central Edge Gateway Agent active.")
        except Exception as e:
            logger.warning(f"MQTT connect failed: {e}. Operating in standalone local buffer mode.")

        # Main edge coordination loop
        while True:
            # Check for internet restoration and sync buffered SQLite records
            self.sync.sync_cycle()
            time.sleep(self.config["sync_interval_seconds"])

if __name__ == "__main__":
    agent = GatewayAgent()
    agent.start()

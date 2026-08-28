import asyncio
import json
import logging
from typing import Optional, Any
import paho.mqtt.client as mqtt
from app.core.config import settings
from app.mqtt import handlers

logger = logging.getLogger(__name__)

class MQTTManager:
    """
    Node-agnostic MQTT client manager supporting MINEGATE LoRa Concentrator
    topic hierarchy and legacy sensor topics with automatic reconnection.
    """

    def __init__(self):
        self.client: Optional[mqtt.Client] = None
        self.loop: Optional[asyncio.AbstractEventLoop] = None
        self.is_connected: bool = False

    def _on_connect(self, client, userdata, flags, rc):
        if rc == 0:
            self.is_connected = True
            logger.info(f"Connected successfully to MQTT Broker at {settings.MQTT_BROKER_HOST}:{settings.MQTT_BROKER_PORT}")
            
            # Subscribe to MINEGATE LoRa concentrator topics & node topics
            topics = [
                ("minegate/+/telemetry", 0),
                ("minegate/+/alerts", 1),
                ("minegate/+/status", 0),
                ("minegate/+/commands", 0),
                ("minegate/+/sync", 1),
                ("mine/nodes/+/telemetry", 0),
                ("mine/nodes/+/status", 0),
                ("mine/nodes/+/alert", 1),
                ("mine/nodes/+/mesh", 0),
                ("mine/gateway/status", 0),
            ]
            self.client.subscribe(topics)
            logger.info("Subscribed to MQTT topics: minegate/+/..., mine/nodes/+/...")
        else:
            self.is_connected = False
            logger.error(f"Failed to connect to MQTT broker with result code: {rc}")

    def _on_disconnect(self, client, userdata, rc):
        self.is_connected = False
        if rc != 0:
            logger.warning(f"Unexpected MQTT disconnection (rc={rc}). Auto-reconnect will be attempted.")
        else:
            logger.info("Disconnected from MQTT broker.")

    def _on_message(self, client, userdata, msg):
        topic = msg.topic
        try:
            payload_str = msg.payload.decode("utf-8")
            payload = json.loads(payload_str) if payload_str else {}
        except Exception as e:
            logger.warning(f"Failed to decode MQTT JSON payload on topic '{topic}': {e}")
            return

        if not self.loop or self.loop.is_closed():
            logger.error("Asyncio loop is not active for MQTT dispatch.")
            return

        parts = topic.split("/")

        # 1. MINEGATE Hierarchy: minegate/{gateway_id}/{channel}
        if len(parts) >= 3 and parts[0] == "minegate":
            gateway_id = parts[1]
            channel = parts[2]

            if channel == "telemetry":
                node_identifier = payload.get("node_id") or payload.get("node_code") or "UNKNOWN"
                asyncio.run_coroutine_threadsafe(handlers.handle_telemetry(node_identifier, payload), self.loop)
            elif channel == "alerts":
                node_identifier = payload.get("node_id") or payload.get("node_code") or "GATEWAY"
                asyncio.run_coroutine_threadsafe(handlers.handle_alert(node_identifier, payload), self.loop)
            elif channel == "status":
                asyncio.run_coroutine_threadsafe(handlers.handle_gateway_status(payload), self.loop)

        # 2. Legacy / Node-Direct Hierarchy: mine/nodes/{node_id}/{action}
        elif len(parts) >= 4 and parts[0] == "mine" and parts[1] == "nodes":
            node_id = parts[2]
            action = parts[3]

            if action == "telemetry":
                asyncio.run_coroutine_threadsafe(handlers.handle_telemetry(node_id, payload), self.loop)
            elif action == "status":
                asyncio.run_coroutine_threadsafe(handlers.handle_status(node_id, payload), self.loop)
            elif action == "alert":
                asyncio.run_coroutine_threadsafe(handlers.handle_alert(node_id, payload), self.loop)
            elif action == "mesh":
                asyncio.run_coroutine_threadsafe(handlers.handle_mesh(node_id, payload), self.loop)
        
        elif topic == "mine/gateway/status":
            asyncio.run_coroutine_threadsafe(handlers.handle_gateway_status(payload), self.loop)

    def start(self, loop: asyncio.AbstractEventLoop = None):
        """Initialize and start background MQTT network loop."""
        if loop is None:
            try:
                loop = asyncio.get_running_loop()
            except RuntimeError:
                loop = asyncio.get_event_loop()
        self.loop = loop
        try:
            self.client = mqtt.Client(client_id="mineguard_fastapi_backend", clean_session=True)
            if settings.MQTT_USERNAME and settings.MQTT_PASSWORD:
                self.client.username_pw_set(settings.MQTT_USERNAME, settings.MQTT_PASSWORD)

            self.client.on_connect = self._on_connect
            self.client.on_disconnect = self._on_disconnect
            self.client.on_message = self._on_message

            logger.info(f"Connecting to MQTT broker {settings.MQTT_BROKER_HOST}:{settings.MQTT_BROKER_PORT}...")
            self.client.connect_async(settings.MQTT_BROKER_HOST, settings.MQTT_BROKER_PORT, keepalive=settings.MQTT_KEEPALIVE)
            self.client.loop_start()
        except Exception as e:
            logger.warning(f"Could not start MQTT client (running in offline/disconnected mode): {e}")

    def stop(self):
        """Stop MQTT client loop gracefully."""
        if self.client:
            try:
                self.client.loop_stop()
                self.client.disconnect()
                logger.info("MQTT client loop stopped.")
            except Exception as e:
                logger.warning(f"Error stopping MQTT client: {e}")

    def publish(self, topic: str, payload: Any, qos: int = 0, retain: bool = False):
        """Publish a message downlink to the MQTT broker."""
        if not self.client or not self.is_connected:
            logger.warning(f"Cannot publish to {topic}: MQTT client not connected.")
            return False

        try:
            payload_str = json.dumps(payload) if isinstance(payload, (dict, list)) else str(payload)
            self.client.publish(topic, payload_str, qos=qos, retain=retain)
            logger.info(f"Published MQTT message to '{topic}'")
            return True
        except Exception as e:
            logger.error(f"Error publishing to MQTT topic '{topic}': {e}")
            return False

# Global singleton instance
mqtt_manager = MQTTManager()
mqtt_client = mqtt_manager

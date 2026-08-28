import json
import logging
from gateway.config import GATEWAY_CONFIG
from gateway.field_transport import SimulatedFieldTransportAdapter, FieldTransportAdapter

logger = logging.getLogger("NodeLocator")

class NodeLocatorAdapter:
    """
    Bidirectional Node Locator:
    Sends downlink command over LoRa to the target MINEGUARD node.
    Target node triggers local piezo buzzer and ultra-bright flashing strobe LED.
    """
    def __init__(self, mqtt_client=None, transport: FieldTransportAdapter = None):
        self.client = mqtt_client
        self.transport = transport or SimulatedFieldTransportAdapter(node_count=20, gateway_id=GATEWAY_CONFIG["gateway_id"])

    def locate_node(self, node_id: str, duration_sec: int = 10):
        # 1. Dispatch over Field Transport (Simulated or SX1302 LoRa)
        res = self.transport.locate_node(node_id, duration_sec)

        # 2. Also publish downlink command to MQTT topic
        if self.client:
            topic = f"minegate/{GATEWAY_CONFIG['gateway_id']}/commands"
            payload = json.dumps({
                "command": "LOCATE_NODE",
                "target_node": node_id,
                "duration_seconds": duration_sec,
                "gateway_id": GATEWAY_CONFIG["gateway_id"]
            })
            self.client.publish(topic, payload)
            # Legacy fallback topic
            self.client.publish(f"mine/nodes/{node_id}/locate", payload)
            logger.info(f"Published LOCATE command for {node_id} on topic {topic}")

        return res

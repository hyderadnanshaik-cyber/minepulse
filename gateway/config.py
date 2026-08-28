import os

GATEWAY_CONFIG = {
    "gateway_id": os.getenv("GATEWAY_ID", "MINEGATE-01"),
    "device_id": os.getenv("GATEWAY_DEVICE_ID", "RPI-ZERO2W-001"),
    "name": "MINEGATE — Raspberry Pi Zero 2 W Central LoRa Gateway",
    "hardware": "Raspberry Pi Zero 2 W + SX1302/SX1303 LoRa Concentrator",
    "concentrator_model": "SX1302/SX1303 8-Channel LoRa Concentrator",
    "lora_frequency_mhz": float(os.getenv("LORA_FREQ_MHZ", "868.1")),
    "mqtt_host": os.getenv("MQTT_HOST", "localhost"),
    "mqtt_port": int(os.getenv("MQTT_PORT", 1883)),
    "local_api_url": os.getenv("LOCAL_API_URL", "http://localhost:8000/api"),
    "cloud_api_url": os.getenv("CLOUD_API_URL", "https://api.mineguard.cloud/api"),
    "db_path": os.getenv("GATEWAY_DB_PATH", "gateway/edge_buffer.db"),
    "alarm_pin": int(os.getenv("ALARM_GPIO_PIN", 18)),  # GPIO 18 for local Siren/Strobe Relay
    "sync_interval_seconds": 15,
    "lora_channels": 8
}

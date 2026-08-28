# MINEGUARD MQTT Topic Architecture
## SIH26025 — Internal Gateway-to-Backend Broker Design

> **Important**: MQTT operates **after** the MINEGATE Raspberry Pi Zero 2 W gateway. It translates physical LoRa RF packets into decoupled microservice streams.

---

### Topic Hierarchy

| Topic | Publisher | Subscribers | Description |
|-------|-----------|-------------|-------------|
| `minegate/{gateway_id}/telemetry` | MINEGATE Agent | FastAPI, ML Engine, WS Broadcaster | Ingests real-time LoRa sensor frames from nodes |
| `minegate/{gateway_id}/alerts` | MINEGATE Agent | FastAPI, Alarm Dispatcher | Critical hardware trips and risk threshold violations |
| `minegate/{gateway_id}/status` | MINEGATE Agent | FastAPI, Health Monitor | Gateway CPU, RAM, Temp, SQLite status, LoRa status |
| `minegate/{gateway_id}/commands` | FastAPI / PWA | MINEGATE Agent | Downlink commands (e.g. `LOCATE_NODE`, `ACTIVATE_ALARM`) |
| `minegate/{gateway_id}/sync` | MINEGATE Agent | Sync Service | Cloud synchronization trigger & queue status |

---

### Sample Downlink Locator Command Payload
```json
{
  "command": "LOCATE_NODE",
  "target_node": "NODE_19",
  "duration_seconds": 10,
  "gateway_id": "MINEGATE-01"
}
```

# RED HACK REST API & WebSocket Specification

## 1. Overview & Authentication

The RED HACK backend exposes RESTful API endpoints and real-time WebSockets powered by FastAPI.
- **Base URL**: `http://localhost:8000/api/v1` (Cloud / Local Dev) or `http://192.168.4.1:8000/api/v1` (Offline Edge Gateway)
- **Interactive Swagger Docs**: `http://localhost:8000/docs`
- **Interactive ReDoc**: `http://localhost:8000/redoc`

### Authentication Scheme
Protected endpoints require a Firebase ID Token passed as a Bearer token in the `Authorization` header:
```http
Authorization: Bearer <FIREBASE_ID_TOKEN>
```
*Note: In offline edge mode when WAN is disabled, the gateway accepts local API keys configured via `X-Gateway-Key` or cached local session tokens.*

---

## 2. API Endpoints by Domain

### 2.1 Nodes & Hardware Provisioning

#### `GET /api/v1/nodes`
Retrieve all registered sensor nodes, current risk score, battery, and mesh status.
- **Query Params**: `panel_id` (optional), `status` (optional)
- **Response 200 OK**:
```json
[
  {
    "id": "c7a8b9e0-1234-4567-89ab-cdef01234567",
    "device_id": "ESP32_B4E62D1A9F10",
    "node_code": "NODE-001",
    "name": "Intake Drift Stope A1",
    "panel_id": "987fcdeb-51a2-43f1-b89a-0987654321fe",
    "latitude": 23.7957,
    "longitude": 86.4304,
    "sensor_types": ["tilt", "displacement", "vibration", "crack"],
    "status": "ONLINE",
    "risk_level": "NORMAL",
    "risk_score": 14.5,
    "battery": 96.0,
    "signal_strength": -68.0,
    "hop_count": 1,
    "parent_node_id": null,
    "last_seen": "2026-08-26T12:00:00Z"
  }
]
```

#### `POST /api/v1/nodes/register`
Claim and provision a physical node using its 6-digit rolling pairing code.
- **Request Body**:
```json
{
  "code": "100004",
  "name": "Longwall Face Section B",
  "panel_id": "987fcdeb-51a2-43f1-b89a-0987654321fe",
  "latitude": 23.7961,
  "longitude": 86.4312,
  "sensor_types": ["tilt", "displacement", "crack"]
}
```
- **Response 201 Created**:
```json
{
  "success": true,
  "node_id": "a1b2c3d4-e5f6-7a8b-9c0d-1e2f3a4b5c6d",
  "node_code": "NODE-004",
  "status": "REGISTERED"
}
```

#### `POST /api/v1/nodes/{node_id}/locate`
Trigger optical LED strobe and audible buzzer on target ESP32 to physically find it in darkness.
- **Request Body**:
```json
{
  "duration_seconds": 15,
  "buzzer_enabled": true
}
```
- **Response 200 OK**:
```json
{
  "success": true,
  "message": "Locate command dispatched to node NODE-004 via mesh root",
  "dispatched_at": "2026-08-26T12:05:00Z"
}
```

---

### 2.2 Telemetry & Sensor Readings

#### `GET /api/v1/telemetry/latest`
Get latest telemetry snapshot for all active nodes.

#### `GET /api/v1/telemetry/history`
Query time-series telemetry data with aggregation.
- **Query Params**: `node_id`, `start_time`, `end_time`, `interval` (`1m`, `5m`, `1h`)
- **Response 200 OK**:
```json
{
  "node_code": "NODE-001",
  "count": 120,
  "readings": [
    {
      "timestamp": "2026-08-26T12:00:00Z",
      "tilt": 1.25,
      "displacement": 3.4,
      "vibration": 0.04,
      "crack_status": false,
      "battery": 95.5
    }
  ]
}
```

---

### 2.3 Alerts & Evacuation Protocols

#### `GET /api/v1/alerts`
Retrieve active and historical safety alerts.
- **Query Params**: `severity` (`WARNING`, `CRITICAL`, `EVACUATE`), `status` (`DETECTED`, `ACKNOWLEDGED`, `RESOLVED`)

#### `POST /api/v1/alerts/{alert_id}/acknowledge`
Acknowledge an ongoing alert.
- **Request Body**:
```json
{
  "notes": "Inspector dispatched to verify pillar convergence at Panel Alpha."
}
```

#### `POST /api/v1/alerts/evacuate`
Initiate immediate emergency evacuation for a working panel.
- **Request Body**:
```json
{
  "panel_id": "987fcdeb-51a2-43f1-b89a-0987654321fe",
  "reason": "Rapid acceleration of roof strata tilt (>5 deg/min) detected across 3 nodes.",
  "activate_siren": true
}
```
- **Response 200 OK**:
```json
{
  "success": true,
  "action_id": "456e7890-12ab-cdef-3456-7890abcdef12",
  "siren_status": "ACTIVATED",
  "timestamp": "2026-08-26T12:10:00Z"
}
```

---

### 2.4 Gateway & Hardware Alarm Control

#### `GET /api/v1/gateway/status`
Returns edge appliance hardware metrics and connectivity state.
- **Response 200 OK**:
```json
{
  "device_id": "GATEWAY-001",
  "status": "ONLINE",
  "cpu_usage": 18.4,
  "ram_usage": 42.1,
  "temperature": 48.2,
  "storage_used": 24.8,
  "mqtt_status": "RUNNING",
  "mesh_status": "CONNECTED",
  "internet_connected": false,
  "alarm_active": false
}
```

#### `POST /api/v1/gateway/siren`
Manual toggle for the Raspberry Pi GPIO Pin 18 siren relay.
- **Request Body**:
```json
{
  "state": true,
  "duration_seconds": 60,
  "reason": "Scheduled shift evacuation drill"
}
```

---

### 2.5 Machine Learning & Risk Predictions

#### `GET /api/v1/ml/predictions/latest`
Fetch latest Isolation Forest anomaly scores and composite risk index.

#### `POST /api/v1/ml/predict`
Run on-demand inference for a synthetic or test sensor vector.
- **Request Body**:
```json
{
  "tilt": 4.8,
  "displacement": 18.2,
  "vibration": 0.35,
  "crack_status": true,
  "dtilt_dt": 0.8
}
```
- **Response 200 OK**:
```json
{
  "anomaly_score": 0.88,
  "is_anomaly": true,
  "risk_score": 91.4,
  "risk_level": "CRITICAL",
  "confidence": 0.94,
  "model_version": "v1.2.0-iforest"
}
```

---

## 3. Real-Time WebSockets

### 3.1 Live Telemetry Stream
- **URL**: `ws://localhost:8000/ws/telemetry`
- **Protocol**: JSON payload pushed on every MQTT sensor event.
- **Message Example**:
```json
{
  "event": "TELEMETRY_UPDATE",
  "node_id": "NODE-002",
  "timestamp": "2026-08-26T12:15:30Z",
  "metrics": {
    "tilt": 2.1,
    "displacement": 8.4,
    "vibration": 0.05,
    "crack": false,
    "battery": 92
  },
  "risk": {
    "score": 28.0,
    "level": "LOW"
  }
}
```

### 3.2 Live Safety Alert Stream
- **URL**: `ws://localhost:8000/ws/alerts`
- **Pushes**: High-priority alert state changes, siren triggers, and evacuation orders.

### 3.3 Mesh Topology Stream
- **URL**: `ws://localhost:8000/ws/mesh`
- **Pushes**: Node join/leave events, parent re-routing, and RSSI link updates.

---

## 4. Standard Error Responses

```json
{
  "status_code": 404,
  "error": "Not Found",
  "message": "Sensor node with ID 'NODE-999' not found in active registry.",
  "timestamp": "2026-08-26T12:00:00Z"
}
```

# MINEGUARD — FLUTTER, BACKEND, DATABASE, HARDWARE, MQTT & CLOUD ARCHITECTURE
### Team: RED HACK | SIH Problem: SIH26025 | Mine: Jharia Coalfield, Dhanbad, Jharkhand

---

## SECTION 1: FLUTTER

### Why Flutter?
The MINEGUARD system needs to reach two audiences: desktop control-room operators (best served by a web PWA) and field safety officers who are mobile. Flutter is Google's cross-platform framework that compiles a single Dart codebase to native Android and iOS applications. **We chose Flutter over React Native** because: (1) Flutter compiles to native ARM code (not a JS bridge), giving better performance for real-time sensor data rendering; (2) `flutter_map` provides OpenStreetMap GIS mapping without Google Maps billing; (3) Flutter's `fl_chart` library delivers smooth, GPU-accelerated sensor waveform charts.

### Flutter Status: PARTIALLY IMPLEMENTED

Flutter code EXISTS. Models, Riverpod providers, screen skeletons, widgets, and `main.dart` are all written. The providers are correctly wired to the FastAPI API and WebSocket. However, there is no `android/` directory yet — this means the app cannot be compiled to an APK without one additional `flutter create` step.

**File**: `flutter_app/pubspec.yaml` (46 lines)
```yaml
name: mineguard
description: "AI-Enabled Real-Time Mine Subsidence Monitoring, Prediction & Early Warning System"
sdk: '>=3.2.0 <4.0.0'
```

### Flutter Dependencies — Why Each Package?

| Package | Version | WHY WE CHOSE IT | Purpose in MINEGUARD |
|---|---|---|---|
| `flutter_riverpod` | ^2.5.1 | Riverpod is the successor to Provider, solving the `BuildContext` scope problem. For a real-time app with WebSocket state flowing into multiple screens simultaneously, Riverpod's `StreamProvider` and `StateNotifierProvider` handle async data cleanly without rebuilding the whole widget tree. | Global state: nodes, alerts, telemetry, predictions, gateway status |
| `dio` | ^5.4.3 | Dio supports request interceptors (auto-inject Bearer token), cancellation tokens (cancel in-flight requests when screen closes), and `FormData` for future file uploads. Flutter's built-in `http` package lacks interceptors. | All REST API calls to FastAPI backend |
| `web_socket_channel` | ^2.4.5 | Official Dart package for WebSocket streams. Integrates with Riverpod's `StreamProvider` for reactive UI updates — when a new sensor reading arrives, the UI rebuilds only the affected widgets. | Live telemetry feed from `ws://[host]:8000/ws/telemetry` |
| `flutter_map` | ^6.1.0 | OpenStreetMap-based mapping without Google Maps API key or billing. Critical for deployment in remote mining areas. Supports custom markers, polygons (subsidence zone), and polylines. | GIS mine map screen with node markers and impact zones |
| `fl_chart` | ^0.68.0 | GPU-accelerated, pure-Flutter chart library. Renders smooth LineCharts for 10+ sensor parameters updating every 30 seconds. No WebView dependency. | Sensor waveform charts: displacement, tilt, vibration time series |
| `shared_preferences` | ^2.2.3 | Lightweight key-value storage for persisting language selection, last-viewed node, and auth token between app sessions. | Local settings persistence on the device |
| `intl` | ^0.19.0 | Official Dart internationalization library. Handles date/time formatting (e.g., "2026-08-28T23:07:00" → "28 Aug 2026, 11:07 PM IST") and number formatting for sensor readings. | Date and number formatting throughout the app |

**`flutter_app/lib/main.dart` (47 lines) — Purpose:**
```dart
// Lines 10–16: Entry point
void main() {
  WidgetsFlutterBinding.ensureInitialized();
  runApp(const ProviderScope(child: MineGuardApp()));
}
```
`ProviderScope` wraps the entire app — this is Riverpod's requirement, making all providers accessible from any widget. Line 23 reads the locale from Riverpod, enabling real-time language switching.

**Existing Flutter Files (VERIFIED):**
| File | Size | Purpose |
|---|---|---|
| `lib/main.dart` | 1,287 bytes | App entry. MaterialApp with 3 locales (en, hi, ur) |
| `lib/models/telemetry_model.dart` | 3,416 bytes | Mirrors FastAPI `SensorReading` schema for type-safe JSON parsing |
| `lib/models/alert_model.dart` | 1,519 bytes | Mirrors FastAPI `Alert` schema |
| `lib/models/node_model.dart` | 1,801 bytes | Mirrors FastAPI `Node` schema |
| `lib/models/prediction_model.dart` | 1,751 bytes | Mirrors FastAPI `AIPrediction` schema |
| `lib/models/gateway_model.dart` | 1,777 bytes | Mirrors FastAPI `Gateway` schema |
| `lib/providers/telemetry_provider.dart` | 1,633 bytes | **WIRED**: Calls REST API + subscribes to WebSocket |
| `lib/providers/alert_provider.dart` | 1,276 bytes | Fetches and streams alerts |
| `lib/providers/node_provider.dart` | 584 bytes | Node list state |
| `lib/widgets/subsidence_alert_dialog.dart` | 5,551 bytes | Full-screen critical evacuation dialog |
| `lib/widgets/metric_card.dart` | 3,231 bytes | Reusable KPI display card |
| `lib/widgets/risk_badge.dart` | 1,335 bytes | Color-coded NORMAL/MODERATE/HIGH/CRITICAL badge |

**IMPORTANT — `telemetry_provider.dart` IS wired to live API** (lines 17–36):
```dart
Future<void> fetchInitialTelemetry() async {
    final res = await apiClient.get(ApiConstants.telemetry);  // REST GET
}
void listenToLiveWebSocket() {
    wsClient.telemetryStream.listen((data) {
        final model = TelemetryModel.fromJson(data);
        state = {...state, model.nodeCode: model};  // Riverpod state update
    });
}
```

---

## SECTION 2: BACKEND ARCHITECTURE

### Why FastAPI?

**FastAPI was chosen over Django, Flask, and Express.js because:**
1. **Native async/await**: Mine telemetry involves hundreds of concurrent connections (WebSockets, MQTT callbacks, DB writes). FastAPI runs on Uvicorn ASGI, handling all I/O concurrently without blocking threads.
2. **Python ecosystem**: The AI/ML pipeline uses scikit-learn, numpy, and pandas — all Python. Using FastAPI means the ML inference runs IN the same process as the API, with zero inter-process latency.
3. **Auto-generated OpenAPI docs**: FastAPI automatically generates `/docs` and `/redoc` API documentation from type hints. During SIH demos, judges can explore all API endpoints interactively.
4. **Pydantic validation**: All incoming sensor JSON is validated by Pydantic schemas before touching the database. Malformed sensor packets are rejected cleanly.

**Framework**: FastAPI (Python)
**Entry Point**: `backend/main.py` (400 lines)
**ASGI Server**: Uvicorn
**Port**: 8000

### Architecture Pattern

```
frontend/Flutter
    ↓  HTTP REST + WebSocket
backend/main.py (FastAPI app + lifespan context manager)
    ↓  includes 13 routers from
backend/app/api/*.py (one file per domain = separation of concerns)
    ↓  calls
backend/app/services/*.py (all business logic isolated here)
    ↓  uses
backend/app/models/*.py (SQLAlchemy ORM — one class per DB table)
    ↓  reads/writes
PostgreSQL 18 + PostGIS (spatial data support)
```

### Backend Startup Sequence (`main.py` lines 284–313)
The `lifespan()` async context manager runs on startup:
1. `verify_and_seed_postgres()` (line 288): Creates the 20 nodes, gateway, mine config, and 10 infrastructure assets if they don't exist.
2. `mqtt_client.start(loop)` (line 293): Connects to Mosquitto MQTT broker on port 1883 for hardware node communication.
3. `asyncio.create_task(_auto_escalation_loop())` (line 299): Spawns a background task that loops every 60 seconds, finds unacknowledged CRITICAL alerts, and re-sends email/SMS notifications.

### All 13 API Routers (main.py lines 331–343)

| Router File | Prefix | Why It Exists |
|---|---|---|
| `nodes.py` | `/api/nodes` | CRUD for the 20 ESP32 sensor nodes — registration, status, location |
| `telemetry.py` | `/api/telemetry` | Ingest sensor readings from hardware/gateway/simulator |
| `alerts.py` | `/api/alerts` | List, detail, acknowledge, and escalate alerts |
| `ai.py` | `/api/ai` | Run inference, get predictions, retrain model |
| `gis.py` | `/api/gis` | Serve GeoJSON for the mine map (nodes, zones, infrastructure) |
| `mesh.py` | `/api/mesh` | LoRa mesh topology — which nodes can hear each other |
| `gateway.py` | `/api/gateway` | Gateway status, commands (ACTIVATE_ALARM, LOCATE_NODE) |
| `system.py` | `/api/system` | Backend health check, version, uptime |
| `sync.py` | `/api/sync` | Edge-to-cloud data sync status |
| `reports.py` | `/api/reports` | PDF/CSV historical telemetry export |
| `simulation.py` | `/api/simulation` | Control the 20-node Python simulator |
| `notifications.py` | `/api/notifications` | Email/SMS queue, connectivity status, officer config |
| `infrastructure.py` | `/api/infrastructure` | CRUD for mine infrastructure assets |

### WebSocket Endpoints (main.py lines 346–381)

| Channel | Path | Why Separate |
|---|---|---|
| Telemetry | `/ws/telemetry` | High-frequency (every 30s per node × 20 nodes). Separate to avoid flooding alert subscribers. |
| Alerts | `/ws/alerts` | Low-frequency but high-priority. UI shows instant red notification when new alert arrives. |
| Mesh | `/ws/mesh` | LoRa mesh topology changes. Separate to keep mesh visualization independent. |
| Gateway | `/ws/gateway` | Gateway heartbeat and status changes. |

---

## SECTION 3: MQTT INFRASTRUCTURE & DISPATCH PIPELINE (DEEP DIVE)

### Why MQTT (Message Queuing Telemetry Transport)?
Underground mines are severe RF-challenged environments. Direct HTTP/REST from underground nodes to the cloud is impossible because:
1. **Header Overhead**: HTTP headers consume ~500–1000 bytes per request. LoRa packet payloads are capped at ~222 bytes. MQTT packet headers are as small as **2 bytes**, maximizing telemetry payload capacity.
2. **Connection Persistence**: HTTP requires TCP handshake overhead per request. MQTT maintains lightweight persistent sessions over TCP/IP between the Gateway and the Mosquitto Broker.
3. **Asynchronous Publish/Subscribe**: Decouples physical sensor nodes from FastAPI consumers. Nodes broadcast telemetry without waiting for database operations to finish.
4. **QoS (Quality of Service) Guarantees**: Allows tuning delivery guarantees (QoS 0 for periodic sensor data vs QoS 1 for life-critical alerts and edge-buffer synchronization).

---

### MQTT Architecture & Threading Model
**Files**: `backend/app/mqtt/client.py` (150 lines), `backend/app/mqtt/handlers.py` (162 lines), `mosquitto/mosquitto.conf`

```
 [ESP32 Sensor Nodes]
       ↓ (865.2 MHz LoRa IN865 RF Packets)
 [Raspberry Pi Gateway / LoRa Concentrator]
       ↓ (Paho MQTT Client Publish over Ethernet / 4G)
 [Mosquitto Broker (Port 1883 / Port 9001 WS)]
       ↓ (TCP Subscriptions)
 [FastAPI MQTTManager (paho.mqtt.client background thread)]
       ↓ asyncio.run_coroutine_threadsafe(handler, event_loop)
 [FastAPI Asyncio Event Loop: handlers.py]
       ↓
  ├── Telemetry Handler → PostgreSQL sensor_readings + AI Service + WebSocket
  ├── Alert Handler     → PostgreSQL alerts + AlertService + Evacuation Logic
  ├── Status Handler    → PostgreSQL nodes (heartbeat, battery, RSSI, parent)
  ├── Mesh Handler      → PostgreSQL mesh_connections (multi-hop graph)
  └── Gateway Handler   → PostgreSQL gateways (CPU, RAM, temp, edge status)
```

---

### Topic Hierarchy & QoS Matrix

**Source of Truth**: `backend/app/mqtt/client.py` lines 28–41

MINEGUARD implements a clean two-tier hierarchical topic structure:

#### Tier 1: MINEGATE LoRa Concentrator Hierarchy
Used when the Raspberry Pi Concentrator aggregates and packages telemetry from underground clusters:
| Topic Pattern | QoS | Direction | Purpose |
|---|---|---|---|
| `minegate/+/telemetry` | QoS 0 | Uplink | Ingests aggregated multi-node sensor frames. |
| `minegate/+/alerts` | QoS 1 | Uplink | **High-priority** hardware alert trip (break-wire snapped, seismic shock). |
| `minegate/+/status` | QoS 0 | Uplink | Gateway system health metrics (CPU, RAM, storage, LTE status). |
| `minegate/+/commands` | QoS 0 | Downlink | Gateway commands (`ACTIVATE_ALARM`, `LOCATE_NODE`, `TRIGGER_STROBE`). |
| `minegate/+/sync` | QoS 1 | Uplink | Replayed batches of offline buffered records from SQLite. |

#### Tier 2: Direct Node Hierarchy
Used for individual node addressing and simulation:
| Topic Pattern | QoS | Direction | Purpose |
|---|---|---|---|
| `mine/nodes/+/telemetry` | QoS 0 | Uplink | Direct single-node telemetry packets. |
| `mine/nodes/+/status` | QoS 0 | Uplink | Node heartbeat, battery voltage, hop count. |
| `mine/nodes/+/alert` | QoS 1 | Uplink | Direct hardware emergency alert from specific node code. |
| `mine/nodes/+/mesh` | QoS 0 | Uplink | Node neighbor RSSI survey for dynamic graph construction. |
| `mine/gateway/status` | QoS 0 | Uplink | Global gateway health channel. |

---

### Bridge Architecture: Paho Thread to Asyncio Loop
**File**: `backend/app/mqtt/client.py` lines 53–98

Paho-MQTT runs its network loop on an internal OS thread (`client.loop_start()`). FastAPI runs on an async `asyncio` event loop. Calling async database functions directly from Paho's thread would cause race conditions and event loop deadlocks.

**Solution (`client.py` lines 75, 88, 97)**:
```python
asyncio.run_coroutine_threadsafe(
    handlers.handle_telemetry(node_identifier, payload), 
    self.loop
)
```
This safely transfers incoming MQTT messages from the synchronous Paho background thread into FastAPI's asynchronous event loop!

---

### Handlers Breakdown (`backend/app/mqtt/handlers.py`)

#### 1. `handle_telemetry(node_identifier, payload)` (lines 29–88)
- **Input**: Node ID + Full JSON payload containing:
  - **MPU9250 9-Axis**: `tilt`, `tilt_x`, `tilt_y`, `vibration`, `accel_x/y/z`, `gyro_x/y/z`, `mag_x/y/z`
  - **BME280 Environment**: `temperature`, `humidity`, `pressure`
  - **Ground Displacement**: `displacement`, `displacement_rate`, `displacement_baseline`
  - **Crack Gauge**: `crack_detected`, `crack_status`, `crack_width`
  - **RF & Mesh**: `rssi`, `snr`, `frequency_mhz` (865.2), `spreading_factor` (7), `hop_count`, `route`
- **Actions**:
  1. Validates payload via Pydantic `TelemetryIngestPayload`
  2. Inserts record into `sensor_readings` table via `TelemetryService.ingest_reading(db, ingest_data)`
  3. Triggers `AIService.evaluate_reading()` for ML IsolationForest scoring + DGMS statutory checks
  4. Pushes real-time update to all WebSocket subscribers via `ws_manager.broadcast_telemetry()`

#### 2. `handle_alert(node_identifier, payload)` (lines 109–125)
- **Input**: Alert payload with `alert_type`, `severity` (CRITICAL), `risk_score`, `local_alarm_activated`.
- **Actions**: Calls `AlertService.create_alert()`. Automatically enqueues notification in `NotificationQueue` and activates sirens.

#### 3. `handle_status(node_identifier, payload)` (lines 89–108)
- **Input**: Node heartbeat containing battery level, signal strength (RSSI), parent node ID, hop count.
- **Actions**: Updates the `nodes` table in PostgreSQL, resetting `last_seen` to `datetime.now()`.

#### 4. `handle_mesh(node_identifier, payload)` (lines 126–145)
- **Input**: Dynamic routing tables (`neighbors`, `route`, `hop_count`, `parent_node_id`).
- **Actions**: Calls `MeshService.update_mesh_connections()` to dynamically redraw the mesh topology in the database.

#### 5. `handle_gateway_status(payload)` (lines 146–162)
- **Input**: Gateway CPU, RAM, temperature, storage, internet connectivity status.
- **Actions**: Calls `GatewayService.update_gateway_metrics()`.

---

## SECTION 4: DATABASE

### Why PostgreSQL Over Other Options?

**vs MongoDB**: Mine telemetry is highly structured (fixed sensor columns, foreign key relationships between nodes → readings → alerts → predictions). PostgreSQL's relational model enforces data integrity.

**vs Firebase Firestore**: Firestore doesn't support spatial queries. PostgreSQL with the PostGIS extension can answer "which infrastructure assets are within 300 meters of this node?" with a single spatial query.

**Engine**: PostgreSQL 18 + PostGIS
**ORM**: SQLAlchemy 2.x (async via `asyncpg`)

**Connection Pool (`database.py` lines 23–32)**:
```python
pool_size=30, max_overflow=50, pool_timeout=60, pool_recycle=1800
```

### Database Tables (17 Models)

| Model Class | Table | Why It Exists |
|---|---|---|
| `Panel` | `panels` | Organizes nodes into mine panel sections (evacuation boundaries) |
| `Node` | `nodes` | Stores node identities, GPS coordinates, status, battery, parent node |
| `SensorReading` | `sensor_readings` | Stores raw time-series sensor measurements |
| `AIPrediction` | `ai_predictions` | Stores ML inference results, anomaly scores, spatial patterns |
| `Alert` | `alerts` | Records safety alerts with severity, infrastructure impact, status |
| `AlertAction` | `alert_actions` | Audit log of who acknowledged/escalated which alert and when |
| `InfrastructureAsset` | `infrastructure_assets` | GPS-located mine infrastructure requiring protection |
| `NotificationQueue` | `notification_queue` | Queue of email/SMS notifications with delivery status tracking |
| `Gateway` | `gateways` | Raspberry Pi gateway registration, status, and metrics |
| `MeshConnection` | `mesh_connections` | Dynamic LoRa radio link quality between node pairs |
| `ResponsiblePerson` | `responsible_persons` | Mine safety officers receiving emergency escalations |
| `SyncQueue` | `sync_queue` | Tracks edge-to-cloud sync status for offline data |
| `MineConfig` | `mine_config` | System-wide configuration (timeouts, escalation thresholds) |

---

## SECTION 5: LIVE DATA FLOW — COMPLETE TRACE

```
ESP32 Sensor Node (underground)
    [firmware reads MPU9250 + BME280 + ADS1115 every 3 seconds]
       ↓ LoRa packet at 865.2 MHz (SX1276)
Raspberry Pi Gateway (surface level)
    [Paho MQTT publish to minegate/MINEGATE-01/telemetry or mine/nodes/+/telemetry]
       ↓ Mosquitto MQTT Broker (port 1883)
FastAPI MQTTManager (_on_message callback on background thread)
       ↓ asyncio.run_coroutine_threadsafe(handle_telemetry, loop)
FastAPI Telemetry Handler (handlers.py)
       ↓ SQLAlchemy INSERT into sensor_readings table
AIService.evaluate_reading()
       ↓ Runs IsolationForest inference → calculates risk_score (0–100)
       ↓ Runs Spatial Correlation → evaluates 120m neighbor radius
       ↓ Identifies affected infrastructure within dynamic radius
       ↓ If HIGH/CRITICAL: creates Alert record + triggers notification queue
ws_manager.broadcast_telemetry({type: "AI_SPATIAL_PREDICTION", ...})
       ↓ WebSocket push to all connected browser and mobile clients
React / Flutter UI updates instantaneously (< 2 seconds)
```

---

## SECTION 6: HARDWARE

| Component | WHY THIS SPECIFIC COMPONENT | Code Location |
|---|---|---|
| **ESP32 DevKit V1** | Dual-core 240MHz, 520KB RAM, ultra-low-power deep sleep support, hardware SPI/I2C. | `firmware/src/main.cpp` |
| **MPU9250 9-Axis IMU** | Combined accelerometer + gyroscope + magnetometer in one I2C chip (0x68). Measures tilt angles and micro-seismic vibration RMS. | `main.cpp` lines 95–101 |
| **BME280** | Temperature, humidity, barometric pressure in one I2C package (0x76). Detects water ingress and spontaneous combustion heat. | `main.cpp` lines 103–109 |
| **ADS1115 16-bit ADC** | Precision 16-bit ADC (0x48) overcoming ESP32's noisy internal ADC for micro-volt draw-wire and crack measurements. | `main.cpp` lines 111–118 |
| **Draw-Wire Sensor (A0)** | Measures physical strata displacement in mm (0–50mm range). Primary DGMS statutory monitoring metric. | `main.cpp` line 186 |
| **Potentiometric Crack Gauge (A1)** | Detects surface fissure widening (0–10mm range). | `main.cpp` line 187 |
| **DS3231 RTC** | Hardware battery-backed RTC ensuring microsecond-accurate timestamps when offline. | `main.cpp` lines 120–126 |
| **SX1276 LoRa at 865.2 MHz** | Sub-GHz IN865 band delivering 3–5km rock-penetrating wireless range. | `main.cpp` lines 128–140 |

---

## SECTION 7: RASPBERRY PI GATEWAY & EDGE BUFFER

**File**: `gateway/gateway_agent.py` (103 lines)

- **EdgeLocalDB (`gateway/local_db.py`)**: SQLite edge buffer (`edge_buffer.db`, 377MB). Ensures zero data loss during cloud disconnections.
- **GatewaySyncService (`gateway/sync_service.py`)**: Probes Google DNS TCP port 53 to check for internet restoration and processes batched records.
- **Known Sync Gap**: `sync_service.py` lines 33–37 marks records as `SYNCED` locally but requires the HTTP upload POST call to complete edge-to-cloud sync.

---

## SECTION 8: EMAIL / SMS / NOTIFICATIONS

**File**: `backend/app/services/notification_service.py` (271 lines)

- **EmailJS Integration**: REST POST over HTTPS port 443 — bypasses cloud SMTP port 25 blocking.
- **Twilio SMS**: Carrier-direct SMS for safety officers in low-connectivity areas.
- **Offline Queue**: Unsent alerts persist in `notification_queue` table with `WAITING_FOR_INTERNET`.
- **Auto-Escalation Loop (`main.py` lines 239–282)**: Independent `asyncio.Task` checking every 60s for unacknowledged CRITICAL alerts and re-triggering escalations.

---

## SECTION 9: DOCKER & CLOUD

- **Docker Compose (`docker-compose.yml`)**: 5 isolated microservices (`postgres` with PostGIS 16-3.4, `mosquitto` MQTT broker, `backend` FastAPI, `ml` worker, `simulator`).
- **Azure Strategy (`.env.azure.example`)**: Architecture mapped for Azure Container Apps + Azure Database for PostgreSQL Flexible Server + Azure IoT Hub.

---

## ACTUAL IMPLEMENTATION STATUS — DOCUMENT 2

| Feature | Status | Evidence / File | Notes |
|---|---|---|---|
| FastAPI Backend | IMPLEMENTED / VERIFIED | `backend/main.py` | 13 REST routers active |
| MQTT Manager & Loop | IMPLEMENTED / VERIFIED | `backend/app/mqtt/client.py` | Paho MQTT background client with auto-reconnect |
| MQTT Handlers | IMPLEMENTED / VERIFIED | `backend/app/mqtt/handlers.py` | Full 5-channel dispatch pipeline |
| Mosquitto Broker | IMPLEMENTED / VERIFIED | `docker-compose.yml`, `mosquitto/` | Ports 1883 and 9001 (WS) |
| WebSockets (4 channels) | IMPLEMENTED / VERIFIED | `main.py` lines 346–381 | Live telemetry, alerts, mesh, gateway |
| PostgreSQL 18 + PostGIS | IMPLEMENTED / VERIFIED | `backend/app/models/*.py` | 17 tables, Integer PKs |
| Auto-Escalation Loop | IMPLEMENTED / VERIFIED | `main.py` lines 239–282 | Background asyncio task running every 60s |
| Notification Queue | IMPLEMENTED / VERIFIED | `notification_service.py` | Database persistence with retry status |
| Gateway MQTT Daemon | IMPLEMENTED / VERIFIED | `gateway/gateway_agent.py` | Paho MQTT client active |
| Gateway SQLite Buffer | IMPLEMENTED / VERIFIED | `gateway/local_db.py` | 377MB buffer exists |
| Flutter App Providers | IMPLEMENTED / VERIFIED | `flutter_app/lib/` | Riverpod wired to REST & WebSockets |
| ESP32 Firmware | CONFIGURED / NOT VERIFIED | `firmware/src/main.cpp` | Complete C++ PlatformIO code |
| Docker Compose Stack | IMPLEMENTED / VERIFIED | `docker-compose.yml` | Full 5-service orchestration |

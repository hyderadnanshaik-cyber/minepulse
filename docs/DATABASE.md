# RED HACK Database Architecture & Data Dictionary

## 1. Database Architecture Overview

The system uses **PostgreSQL 16/18 with PostGIS** for high-volume time-series geotechnical metrics, mesh topology tracking, and geospatial GIS queries. In local/offline deployments (Raspberry Pi gateway or micro-controllers), an identical relational schema or SQLite circular buffer is maintained.

### Key Capabilities:
- **Spatial Queries (PostGIS)**: Spatial bounding boxes, point-in-polygon verification for nodes in mine panels (`ST_Contains`), and subsidence impact zones (`ST_Buffer`).
- **High-Throughput Time-Series**: Indexed time-series partition-ready schema for sensor readings.
- **Unified Identifiers**: Compatible with both fast sequential integers (`SERIAL/BIGSERIAL`) and globally unique identifiers (`UUID`) for offline distributed synchronization without ID collisions.

---

## 2. Relational Schema & Table Dictionary

### 2.1 `panels` (Mine Working Panels / Extraction Sections)
Stores geometric boundaries and operational metadata of underground extraction faces and longwall panels.

| Column | Type | Constraints | Description |
| :--- | :--- | :--- | :--- |
| `id` | `UUID` / `SERIAL` | `PRIMARY KEY` | Unique panel identifier |
| `panel_code` | `VARCHAR(32)` | `UNIQUE, NOT NULL`| Code e.g. `PANEL-ALPHA-01` |
| `name` | `VARCHAR(128)` | `NOT NULL` | Descriptive name |
| `description`| `TEXT` | `NULL` | Strata depth, seam thickness notes |
| `boundary` | `GEOMETRY(POLYGON, 4326)` | `NULL` | PostGIS Polygon of panel perimeter |
| `created_at` | `TIMESTAMPTZ` | `DEFAULT NOW()` | Record creation timestamp |
| `updated_at` | `TIMESTAMPTZ` | `DEFAULT NOW()` | Last update timestamp |

---

### 2.2 `nodes` (Sensor Hardware Nodes)
Stores physical and logical properties, coordinates, risk assessments, and mesh routing state.

| Column | Type | Constraints | Description |
| :--- | :--- | :--- | :--- |
| `id` | `UUID` / `SERIAL` | `PRIMARY KEY` | Internal surrogate key |
| `device_id` | `VARCHAR(64)` | `UNIQUE, NOT NULL`| MAC or Hardware UUID (e.g. `ESP32_B4E62D`) |
| `node_code` | `VARCHAR(16)` | `UNIQUE, NOT NULL`| Human-readable code e.g. `NODE-001` |
| `name` | `VARCHAR(128)` | `NOT NULL` | Installation location name |
| `panel_id` | `UUID` / `INTEGER` | `REFERENCES panels(id)` | Associated mine panel |
| `latitude` | `DOUBLE PRECISION`| `NULL` | WGS84 Latitude |
| `longitude` | `DOUBLE PRECISION`| `NULL` | WGS84 Longitude |
| `location` | `GEOMETRY(POINT, 4326)` | `GIST INDEX` | PostGIS Point geometry |
| `sensor_types` | `JSONB` | `DEFAULT '[]'` | Array of sensors: `["tilt", "displacement", "vibration", "crack"]` |
| `status` | `VARCHAR(16)` | `DEFAULT 'OFFLINE'`| `ONLINE`, `OFFLINE`, `WARNING`, `CRITICAL` |
| `risk_level` | `VARCHAR(16)` | `DEFAULT 'NORMAL'` | `NORMAL`, `LOW`, `MEDIUM`, `HIGH`, `CRITICAL` |
| `risk_score` | `FLOAT` | `DEFAULT 0.0` | Computed multi-factor risk score (0 - 100) |
| `battery` | `FLOAT` | `NULL` | Battery percentage (0 - 100%) |
| `last_seen` | `TIMESTAMPTZ` | `NULL` | Last received heartbeat timestamp |
| `hop_count` | `INTEGER` | `NULL` | Number of mesh hops to root node |
| `mesh_route` | `JSONB` | `NULL` | Full route path array |
| `parent_node_id` | `UUID` / `INTEGER` | `REFERENCES nodes(id)` | Direct upstream mesh parent node |
| `signal_strength`| `FLOAT` | `NULL` | RSSI value in dBm |
| `is_registered` | `BOOLEAN` | `DEFAULT TRUE` | Pairing verification status |
| `installation_info` | `TEXT` | `NULL` | Rock bolt depth, anchor type, etc. |
| `created_at` | `TIMESTAMPTZ` | `DEFAULT NOW()` | Registration time |
| `updated_at` | `TIMESTAMPTZ` | `DEFAULT NOW()` | Update timestamp |

---

### 2.3 `node_registration_codes` (Secure Hardware Pairing)
Facilitates 6-digit rolling pairing codes for quick commissioning in underground conditions.

| Column | Type | Constraints | Description |
| :--- | :--- | :--- | :--- |
| `id` | `UUID` / `SERIAL` | `PRIMARY KEY` | Code ID |
| `code` | `VARCHAR(6)` | `UNIQUE, NOT NULL`| 6-digit pairing code (e.g. `100001`) |
| `device_id` | `VARCHAR(64)` | `NULL` | Assigned hardware MAC |
| `node_id` | `UUID` / `INTEGER` | `REFERENCES nodes(id)` | Bound node record |
| `status` | `VARCHAR(16)` | `DEFAULT 'PENDING'`| `PENDING`, `USED`, `EXPIRED` |
| `created_at` | `TIMESTAMPTZ` | `DEFAULT NOW()` | Issue time |
| `expires_at` | `TIMESTAMPTZ` | `NULL` | Expiration deadline |
| `used_at` | `TIMESTAMPTZ` | `NULL` | Claim timestamp |

---

### 2.4 `sensor_readings` (Time-Series Telemetry Stream)
Stores all incoming raw and calibrated sensor data frames from the mesh network.

| Column | Type | Constraints | Description |
| :--- | :--- | :--- | :--- |
| `id` | `UUID` / `BIGSERIAL` | `PRIMARY KEY` | Unique telemetry ID |
| `node_id` | `UUID` / `INTEGER` | `REFERENCES nodes(id), NOT NULL` | Originating node |
| `timestamp` | `TIMESTAMPTZ` | `NOT NULL, INDEX` | Precise measurement timestamp |
| `tilt` | `FLOAT` | `NULL` | Roof tilt angle in degrees ($\theta$) |
| `displacement` | `FLOAT` | `NULL` | Rock strata displacement in mm |
| `vibration` | `FLOAT` | `NULL` | Seismic vibration intensity ($g$) |
| `crack_status` | `BOOLEAN` | `DEFAULT FALSE` | True if continuity broken / crack open |
| `temperature` | `FLOAT` | `NULL` | Ambient temperature ($^\circ$C) |
| `battery` | `FLOAT` | `NULL` | Battery state at reading time |
| `signal_strength`| `FLOAT` | `NULL` | RSSI at reading time |
| `hop_count` | `INTEGER` | `NULL` | Mesh hop depth |
| `latitude` | `DOUBLE PRECISION`| `NULL` | GPS coordinate if available |
| `longitude` | `DOUBLE PRECISION`| `NULL` | GPS coordinate if available |
| `raw_payload` | `JSONB` | `NULL` | Full unparsed JSON string |
| `sync_status` | `VARCHAR(16)` | `DEFAULT 'PENDING'` | `PENDING`, `SYNCED`, `FAILED` |
| `created_at` | `TIMESTAMPTZ` | `DEFAULT NOW()` | Ingestion timestamp |

---

### 2.5 `crack_events` (Rock Fracture Incidents)
High-priority incident log for continuous crack detection line triggers.

| Column | Type | Constraints | Description |
| :--- | :--- | :--- | :--- |
| `id` | `UUID` / `SERIAL` | `PRIMARY KEY` | Event ID |
| `node_id` | `UUID` / `INTEGER` | `REFERENCES nodes(id), NOT NULL` | Node detecting crack |
| `detected_at` | `TIMESTAMPTZ` | `NOT NULL` | Trigger timestamp |
| `severity` | `VARCHAR(16)` | `NULL` | `WARNING`, `CRITICAL`, `RUPTURE` |
| `location` | `GEOMETRY(POINT, 4326)` | `NULL` | PostGIS coordinate |
| `notes` | `TEXT` | `NULL` | Physical visual inspection notes |
| `resolved_at` | `TIMESTAMPTZ` | `NULL` | Resolution timestamp |
| `sync_status` | `VARCHAR(16)` | `DEFAULT 'PENDING'` | Sync indicator |
| `created_at` | `TIMESTAMPTZ` | `DEFAULT NOW()` | Creation timestamp |

---

### 2.6 `mesh_connections` (Dynamic Topology Links)
Maintains current active link graph between neighboring mesh nodes.

| Column | Type | Constraints | Description |
| :--- | :--- | :--- | :--- |
| `id` | `UUID` / `SERIAL` | `PRIMARY KEY` | Connection ID |
| `node_id` | `UUID` / `INTEGER` | `REFERENCES nodes(id)` | Child / Source node |
| `neighbor_id`| `UUID` / `INTEGER` | `REFERENCES nodes(id)` | Parent / Peer node |
| `hop_count` | `INTEGER` | `NULL` | Link distance |
| `signal_strength`| `FLOAT` | `NULL` | Link RSSI |
| `route_path` | `JSONB` | `NULL` | Full upstream path |
| `is_active` | `BOOLEAN` | `DEFAULT TRUE` | Active link indicator |
| `last_seen` | `TIMESTAMPTZ` | `DEFAULT NOW()` | Heartbeat timestamp |
| `created_at` | `TIMESTAMPTZ` | `DEFAULT NOW()` | Link establishment time |

---

### 2.7 `alerts` (Subsidence & Anomaly Events)
Generated alerts with spatial hazard boundary and multi-channel escalation state.

| Column | Type | Constraints | Description |
| :--- | :--- | :--- | :--- |
| `id` | `UUID` / `SERIAL` | `PRIMARY KEY` | Alert ID |
| `node_id` | `UUID` / `INTEGER` | `REFERENCES nodes(id)` | Source node (nullable if multi-node) |
| `alert_type` | `VARCHAR(64)` | `NOT NULL` | `TILT_THRESHOLD`, `SUDDEN_SUBSIDENCE`, `CRACK_RUPTURE`, `AI_ANOMALY` |
| `severity` | `VARCHAR(16)` | `NOT NULL` | `INFO`, `WARNING`, `CRITICAL`, `EVACUATE` |
| `title` | `VARCHAR(256)` | `NOT NULL` | Concise summary |
| `message` | `TEXT` | `NULL` | Detailed description & instructions |
| `risk_score` | `FLOAT` | `NULL` | Computed aggregate risk (0-100) |
| `anomaly_score`| `FLOAT` | `NULL` | ML Isolation Forest score |
| `affected_zone`| `GEOMETRY(POLYGON, 4326)` | `NULL` | Buffer polygon of danger zone |
| `status` | `VARCHAR(32)` | `DEFAULT 'DETECTED'`| `DETECTED`, `ACKNOWLEDGED`, `RESOLVED`, `FALSE_ALARM` |
| `local_alarm_activated`| `BOOLEAN` | `DEFAULT FALSE` | True if GPIO siren was sounded |
| `detected_at` | `TIMESTAMPTZ` | `DEFAULT NOW()` | Occurrence time |
| `acknowledged_at` | `TIMESTAMPTZ` | `NULL` | Acknowledgment time |
| `acknowledged_by` | `UUID` / `INTEGER` | `NULL` | User who acknowledged |
| `resolved_at` | `TIMESTAMPTZ` | `NULL` | Resolution time |
| `sync_status` | `VARCHAR(16)` | `DEFAULT 'PENDING'` | Sync state |
| `created_at` | `TIMESTAMPTZ` | `DEFAULT NOW()` | DB insertion time |

---

### 2.8 `alert_actions` (Audit & Evacuation Trail)
Immutable chronological audit log of human and automated responses to alerts.

| Column | Type | Constraints | Description |
| :--- | :--- | :--- | :--- |
| `id` | `UUID` / `SERIAL` | `PRIMARY KEY` | Action record ID |
| `alert_id` | `UUID` / `INTEGER` | `REFERENCES alerts(id)` | Parent alert |
| `action` | `VARCHAR(64)` | `NOT NULL` | `ACKNOWLEDGE`, `EVACUATE_PANEL`, `SILENCE_SIREN`, `RESOLVE` |
| `performed_by`| `UUID` / `INTEGER` | `NULL` | Operator or `SYSTEM` |
| `notes` | `TEXT` | `NULL` | Justification & operational remarks |
| `created_at` | `TIMESTAMPTZ` | `DEFAULT NOW()` | Action timestamp |

---

### 2.9 `ai_predictions` (Machine Learning Inference Log)
Stores ML inference output, feature importance vectors, and spatial correlation tags.

| Column | Type | Constraints | Description |
| :--- | :--- | :--- | :--- |
| `id` | `UUID` / `SERIAL` | `PRIMARY KEY` | Prediction ID |
| `node_id` | `UUID` / `INTEGER` | `REFERENCES nodes(id)` | Analyzed node |
| `reading_id` | `UUID` / `BIGSERIAL`| `REFERENCES sensor_readings(id)` | Trigger reading |
| `anomaly_score`| `FLOAT` | `NOT NULL` | Normalized Isolation Forest score (0 to 1) |
| `risk_score` | `FLOAT` | `NOT NULL` | Hybrid composite risk index (0 to 100) |
| `risk_level` | `VARCHAR(16)` | `NOT NULL` | `NORMAL`, `LOW`, `MEDIUM`, `HIGH`, `CRITICAL` |
| `confidence` | `FLOAT` | `NULL` | Model confidence metric |
| `features` | `JSONB` | `NULL` | Feature vector snapshot |
| `model_version`| `VARCHAR(32)`| `NULL` | Model version tag (e.g. `v1.2.0-iforest`) |
| `spatial_pattern`| `JSONB` | `NULL` | Multi-node neighbor correlation data |
| `created_at` | `TIMESTAMPTZ` | `DEFAULT NOW()` | Prediction time |
| `sync_status` | `VARCHAR(16)` | `DEFAULT 'PENDING'` | Sync state |

---

### 2.10 `gateway` (Edge Hardware Appliance Telemetry)
Stores operating metrics, CPU temperatures, and connectivity states for the Raspberry Pi edge unit.

| Column | Type | Constraints | Description |
| :--- | :--- | :--- | :--- |
| `id` | `UUID` / `SERIAL` | `PRIMARY KEY` | Gateway ID |
| `name` | `VARCHAR(128)` | `DEFAULT 'Main Gateway'`| Appliance name |
| `device_id` | `VARCHAR(64)` | `UNIQUE` | Hardware serial / MAC |
| `ip_address` | `VARCHAR(64)` | `NULL` | Local IP (e.g. `192.168.4.1`) |
| `status` | `VARCHAR(16)` | `DEFAULT 'OFFLINE'`| `ONLINE`, `OFFLINE`, `DEGRADED` |
| `cpu_usage` | `FLOAT` | `NULL` | CPU load percentage |
| `ram_usage` | `FLOAT` | `NULL` | RAM utilization percentage |
| `temperature`| `FLOAT` | `NULL` | Core SoC temperature in $^\circ$C |
| `storage_used`| `FLOAT` | `NULL` | Disk space consumed percentage |
| `mqtt_status`| `VARCHAR(16)` | `NULL` | Mosquitto daemon health |
| `mesh_status`| `VARCHAR(16)` | `NULL` | Root mesh link status |
| `db_status` | `VARCHAR(16)` | `NULL` | PostgreSQL / SQLite health |
| `internet_connected`| `BOOLEAN`| `DEFAULT FALSE` | Cloud reachability flag |
| `cloud_sync_status`| `VARCHAR(16)`| `NULL` | Sync engine status |
| `alarm_active`| `BOOLEAN` | `DEFAULT FALSE` | True if GPIO 18 siren relay is active |
| `last_seen` | `TIMESTAMPTZ` | `NULL` | Heartbeat timestamp |
| `updated_at` | `TIMESTAMPTZ` | `DEFAULT NOW()` | Update timestamp |

---

### 2.11 `gateway_events` (Edge Diagnostics & State Transitions)
Audit table for edge gateway restarts, failover triggers, and siren state changes.

| Column | Type | Constraints | Description |
| :--- | :--- | :--- | :--- |
| `id` | `UUID` / `SERIAL` | `PRIMARY KEY` | Event ID |
| `event_type` | `VARCHAR(64)` | `NOT NULL` | `SIREN_ACTIVATED`, `INTERNET_LOST`, `INTERNET_RESTORED`, `MESH_RECONFIG` |
| `description`| `TEXT` | `NULL` | Human readable event details |
| `metadata` | `JSONB` | `NULL` | Diagnostic payload |
| `created_at` | `TIMESTAMPTZ` | `DEFAULT NOW()` | Log timestamp |
| `sync_status` | `VARCHAR(16)` | `DEFAULT 'PENDING'` | Sync indicator |

---

### 2.12 `notification_queue` (Offline-Buffered Emergency Outbox)
Outbox queue holding SMS and email messages pending internet restoration.

| Column | Type | Constraints | Description |
| :--- | :--- | :--- | :--- |
| `id` | `UUID` / `SERIAL` | `PRIMARY KEY` | Message ID |
| `alert_id` | `UUID` / `INTEGER` | `REFERENCES alerts(id)` | Originating alert |
| `type` | `VARCHAR(16)` | `NOT NULL` | `SMS`, `EMAIL`, `WEBHOOK` |
| `recipient` | `VARCHAR(256)` | `NOT NULL` | Phone number or email address |
| `subject` | `VARCHAR(512)` | `NULL` | Email subject line |
| `body` | `TEXT` | `NULL` | Message text |
| `status` | `VARCHAR(16)` | `DEFAULT 'PENDING'`| `PENDING`, `SENT`, `FAILED` |
| `retry_count`| `INTEGER` | `DEFAULT 0` | Transmission attempts |
| `last_attempt`| `TIMESTAMPTZ`| `NULL` | Last retry time |
| `sent_at` | `TIMESTAMPTZ` | `NULL` | Success timestamp |
| `created_at` | `TIMESTAMPTZ` | `DEFAULT NOW()` | Queue insertion time |

---

### 2.13 `sync_queue` (Change Data Capture Sync Queue)
Maintains delta records to be pushed from edge to cloud.

| Column | Type | Constraints | Description |
| :--- | :--- | :--- | :--- |
| `id` | `UUID` / `SERIAL` | `PRIMARY KEY` | Sync job ID |
| `table_name` | `VARCHAR(64)` | `NOT NULL` | Target table (e.g. `sensor_readings`) |
| `record_id` | `UUID` / `INTEGER` | `NOT NULL` | Primary key of referenced record |
| `operation` | `VARCHAR(16)` | `NOT NULL` | `INSERT`, `UPDATE`, `DELETE` |
| `payload` | `JSONB` | `NULL` | Serialized record data |
| `status` | `VARCHAR(16)` | `DEFAULT 'PENDING'`| `PENDING`, `PROCESSING`, `SYNCED`, `FAILED` |
| `retry_count`| `INTEGER` | `DEFAULT 0` | Sync attempts |
| `last_attempt`| `TIMESTAMPTZ`| `NULL` | Last attempt timestamp |
| `created_at` | `TIMESTAMPTZ` | `DEFAULT NOW()` | Enqueue timestamp |

---

### 2.14 `responsible_persons` (Role-Based Access Control)
Stores user contact information, safety role, and links to Firebase Authentication.

| Column | Type | Constraints | Description |
| :--- | :--- | :--- | :--- |
| `id` | `UUID` / `SERIAL` | `PRIMARY KEY` | Person ID |
| `firebase_uid`| `VARCHAR(128)` | `UNIQUE, NOT NULL`| Firebase Auth User ID |
| `email` | `VARCHAR(256)` | `UNIQUE, NOT NULL`| User email address |
| `name` | `VARCHAR(256)` | `NULL` | Full name |
| `role` | `VARCHAR(32)` | `DEFAULT 'VIEWER'` | `ADMIN`, `SAFETY_OFFICER`, `OPERATOR`, `VIEWER` |
| `phone` | `VARCHAR(32)` | `NULL` | Phone number for emergency SMS |
| `is_active` | `BOOLEAN` | `DEFAULT TRUE` | Active authorization state |
| `created_at` | `TIMESTAMPTZ` | `DEFAULT NOW()` | User creation time |
| `updated_at` | `TIMESTAMPTZ` | `DEFAULT NOW()` | Update timestamp |

---

### 2.15 `node_connectivity_events` (Mesh Re-Routing History)
Maintains historical records of topology mutations, parent switches, and disconnections.

| Column | Type | Constraints | Description |
| :--- | :--- | :--- | :--- |
| `id` | `UUID` / `SERIAL` | `PRIMARY KEY` | Event ID |
| `node_id` | `UUID` / `INTEGER` | `REFERENCES nodes(id), NOT NULL` | Node experiencing route change |
| `event_type` | `VARCHAR(32)` | `NOT NULL` | `PARENT_SWITCHED`, `NODE_JOINED`, `NODE_LOST` |
| `old_route` | `JSONB` | `NULL` | Previous route array |
| `new_route` | `JSONB` | `NULL` | New route array |
| `hop_count` | `INTEGER` | `NULL` | New hop count |
| `parent_node_id`| `UUID` / `INTEGER` | `REFERENCES nodes(id)` | New parent node |
| `occurred_at` | `TIMESTAMPTZ` | `DEFAULT NOW()` | Event time |
| `sync_status` | `VARCHAR(16)` | `DEFAULT 'PENDING'` | Sync indicator |

---

## 3. High-Performance Spatial & Time-Series Indexes

```sql
-- Spatial GIST Indexes
CREATE INDEX IF NOT EXISTS idx_nodes_location ON nodes USING GIST(location);
CREATE INDEX IF NOT EXISTS idx_panels_boundary ON panels USING GIST(boundary);
CREATE INDEX IF NOT EXISTS idx_alerts_zone ON alerts USING GIST(affected_zone);

-- High-Frequency Time-Series Filtering
CREATE INDEX IF NOT EXISTS idx_readings_node_time ON sensor_readings(node_id, timestamp DESC);
CREATE INDEX IF NOT EXISTS idx_readings_sync_status ON sensor_readings(sync_status) WHERE sync_status = 'PENDING';

-- Rapid Alert Queries
CREATE INDEX IF NOT EXISTS idx_alerts_status_severity ON alerts(status, severity);
CREATE INDEX IF NOT EXISTS idx_sync_queue_pending ON sync_queue(status, created_at) WHERE status = 'PENDING';
```

-- =================================================================
-- RED HACK Mine Subsidence Monitoring System
-- Database Schema — PostgreSQL 18 + PostGIS
-- Primary Keys: SERIAL / INTEGER (Matches Existing Tables)
-- =================================================================

-- Enable PostGIS spatial extension if not already enabled
CREATE EXTENSION IF NOT EXISTS postgis;

-- -----------------------------------------------------------------
-- 1. PANELS (Mine working panels / sections)
-- -----------------------------------------------------------------
CREATE TABLE IF NOT EXISTS panels (
  id          SERIAL PRIMARY KEY,
  panel_code  VARCHAR(32) UNIQUE NOT NULL,
  name        VARCHAR(128) NOT NULL,
  description TEXT,
  boundary    GEOMETRY(POLYGON, 4326),
  created_at  TIMESTAMPTZ DEFAULT NOW(),
  updated_at  TIMESTAMPTZ DEFAULT NOW()
);

-- -----------------------------------------------------------------
-- 2. NODES (Surface sensor nodes - 20 logical, 4 initial physical)
-- -----------------------------------------------------------------
CREATE TABLE IF NOT EXISTS nodes (
  id                SERIAL PRIMARY KEY,
  device_id         VARCHAR(64) UNIQUE NOT NULL,
  node_code         VARCHAR(16) UNIQUE NOT NULL,
  name              VARCHAR(128) NOT NULL,
  panel_id          INTEGER REFERENCES panels(id) ON DELETE SET NULL,
  latitude          DOUBLE PRECISION,
  longitude         DOUBLE PRECISION,
  location          GEOMETRY(POINT, 4326),
  sensor_types      JSONB DEFAULT '["tilt","displacement","vibration","crack","battery"]'::jsonb,
  status            VARCHAR(16) DEFAULT 'OFFLINE',  -- ONLINE, OFFLINE, WARNING, CRITICAL, DEGRADED
  risk_level        VARCHAR(16) DEFAULT 'NORMAL',   -- NORMAL, WATCH, HIGH, CRITICAL
  risk_score        FLOAT DEFAULT 0.0,
  battery           FLOAT DEFAULT 100.0,
  last_seen         TIMESTAMPTZ,
  hop_count         INTEGER DEFAULT 0,
  mesh_route        JSONB DEFAULT '[]'::jsonb,
  parent_node_id    INTEGER REFERENCES nodes(id) ON DELETE SET NULL,
  signal_strength   FLOAT,
  is_registered     BOOLEAN DEFAULT TRUE,
  installation_info TEXT,
  created_at        TIMESTAMPTZ DEFAULT NOW(),
  updated_at        TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_nodes_location ON nodes USING GIST(location);
CREATE INDEX IF NOT EXISTS idx_nodes_status ON nodes(status);
CREATE INDEX IF NOT EXISTS idx_nodes_panel ON nodes(panel_id);
CREATE INDEX IF NOT EXISTS idx_nodes_code ON nodes(node_code);

-- -----------------------------------------------------------------
-- 3. NODE REGISTRATION CODES (6-digit pairing codes for field deployment)
-- -----------------------------------------------------------------
CREATE TABLE IF NOT EXISTS node_registration_codes (
  id          SERIAL PRIMARY KEY,
  code        VARCHAR(6) UNIQUE NOT NULL,
  device_id   VARCHAR(64),
  node_id     INTEGER REFERENCES nodes(id) ON DELETE CASCADE,
  status      VARCHAR(16) DEFAULT 'PENDING',  -- PENDING, USED, EXPIRED, REVOKED
  created_at  TIMESTAMPTZ DEFAULT NOW(),
  expires_at  TIMESTAMPTZ,
  used_at     TIMESTAMPTZ
);

CREATE INDEX IF NOT EXISTS idx_reg_codes_code ON node_registration_codes(code);

-- -----------------------------------------------------------------
-- 4. SENSOR READINGS (Time-series telemetry from nodes)
-- -----------------------------------------------------------------
CREATE TABLE IF NOT EXISTS sensor_readings (
  id              SERIAL PRIMARY KEY,
  node_id         INTEGER REFERENCES nodes(id) ON DELETE CASCADE NOT NULL,
  timestamp       TIMESTAMPTZ NOT NULL,
  tilt            FLOAT DEFAULT 0.0,
  displacement    FLOAT DEFAULT 0.0,
  vibration       FLOAT DEFAULT 0.0,
  crack_status    BOOLEAN DEFAULT FALSE,
  temperature     FLOAT,
  battery         FLOAT,
  signal_strength FLOAT,
  hop_count       INTEGER DEFAULT 0,
  latitude        DOUBLE PRECISION,
  longitude       DOUBLE PRECISION,
  raw_payload     JSONB,
  sync_status     VARCHAR(16) DEFAULT 'PENDING',  -- PENDING, SYNCED, FAILED
  created_at      TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_readings_node      ON sensor_readings(node_id);
CREATE INDEX IF NOT EXISTS idx_readings_timestamp ON sensor_readings(timestamp DESC);
CREATE INDEX IF NOT EXISTS idx_readings_sync      ON sensor_readings(sync_status);

-- -----------------------------------------------------------------
-- 5. CRACK EVENTS (Ground surface fissure detections)
-- -----------------------------------------------------------------
CREATE TABLE IF NOT EXISTS crack_events (
  id          SERIAL PRIMARY KEY,
  node_id     INTEGER REFERENCES nodes(id) ON DELETE CASCADE NOT NULL,
  detected_at TIMESTAMPTZ NOT NULL,
  severity    VARCHAR(16) DEFAULT 'CRITICAL', -- WARNING, HIGH, CRITICAL
  location    GEOMETRY(POINT, 4326),
  notes       TEXT,
  resolved_at TIMESTAMPTZ,
  sync_status VARCHAR(16) DEFAULT 'PENDING',
  created_at  TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_cracks_node ON crack_events(node_id);

-- -----------------------------------------------------------------
-- 6. MESH CONNECTIONS (Dynamic wireless mesh links between nodes)
-- -----------------------------------------------------------------
CREATE TABLE IF NOT EXISTS mesh_connections (
  id              SERIAL PRIMARY KEY,
  node_id         INTEGER REFERENCES nodes(id) ON DELETE CASCADE NOT NULL,
  neighbor_id     INTEGER REFERENCES nodes(id) ON DELETE CASCADE NOT NULL,
  hop_count       INTEGER DEFAULT 1,
  signal_strength FLOAT,
  route_path      JSONB DEFAULT '[]'::jsonb,
  is_active       BOOLEAN DEFAULT TRUE,
  last_seen       TIMESTAMPTZ DEFAULT NOW(),
  created_at      TIMESTAMPTZ DEFAULT NOW(),
  UNIQUE(node_id, neighbor_id)
);

CREATE INDEX IF NOT EXISTS idx_mesh_node ON mesh_connections(node_id);

-- -----------------------------------------------------------------
-- 7. ALERTS (Real-time safety alarms triggered by rules or AI/ML)
-- -----------------------------------------------------------------
CREATE TABLE IF NOT EXISTS alerts (
  id                     SERIAL PRIMARY KEY,
  node_id                INTEGER REFERENCES nodes(id) ON DELETE SET NULL,
  alert_type             VARCHAR(64) NOT NULL,
  severity               VARCHAR(16) NOT NULL, -- WATCH, WARNING, HIGH, CRITICAL
  title                  VARCHAR(256) NOT NULL,
  message                TEXT,
  risk_score             FLOAT DEFAULT 0.0,
  anomaly_score          FLOAT DEFAULT 0.0,
  affected_zone          GEOMETRY(POLYGON, 4326),
  status                 VARCHAR(32) DEFAULT 'DETECTED', -- DETECTED, ACKNOWLEDGED, UNDER_INVESTIGATION, RESOLVED
  local_alarm_activated  BOOLEAN DEFAULT FALSE,
  detected_at            TIMESTAMPTZ DEFAULT NOW(),
  acknowledged_at        TIMESTAMPTZ,
  acknowledged_by        VARCHAR(128),
  resolved_at            TIMESTAMPTZ,
  sync_status            VARCHAR(16) DEFAULT 'PENDING',
  created_at             TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_alerts_node     ON alerts(node_id);
CREATE INDEX IF NOT EXISTS idx_alerts_severity ON alerts(severity);
CREATE INDEX IF NOT EXISTS idx_alerts_status   ON alerts(status);
CREATE INDEX IF NOT EXISTS idx_alerts_detected ON alerts(detected_at DESC);

-- -----------------------------------------------------------------
-- 8. ALERT ACTIONS (Audit log of operator responses)
-- -----------------------------------------------------------------
CREATE TABLE IF NOT EXISTS alert_actions (
  id           SERIAL PRIMARY KEY,
  alert_id     INTEGER REFERENCES alerts(id) ON DELETE CASCADE NOT NULL,
  action       VARCHAR(64) NOT NULL, -- ACKNOWLEDGE, SILENCE_ALARM, TRIGGER_EVACUATION, RESOLVE
  performed_by VARCHAR(128) NOT NULL, -- Firebase UID or Email
  notes        TEXT,
  created_at   TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_alert_actions_alert ON alert_actions(alert_id);

-- -----------------------------------------------------------------
-- 9. AI PREDICTIONS (Isolation Forest & Risk Engine outputs)
-- -----------------------------------------------------------------
CREATE TABLE IF NOT EXISTS ai_predictions (
  id              SERIAL PRIMARY KEY,
  node_id         INTEGER REFERENCES nodes(id) ON DELETE CASCADE NOT NULL,
  reading_id      INTEGER REFERENCES sensor_readings(id) ON DELETE SET NULL,
  anomaly_score   FLOAT NOT NULL,
  risk_score      FLOAT NOT NULL,
  risk_level      VARCHAR(16) NOT NULL, -- NORMAL, WATCH, HIGH, CRITICAL
  confidence      FLOAT DEFAULT 1.0,
  features        JSONB,
  model_version   VARCHAR(32) DEFAULT 'v1.0.0-isolation-forest',
  spatial_pattern JSONB,
  created_at      TIMESTAMPTZ DEFAULT NOW(),
  sync_status     VARCHAR(16) DEFAULT 'PENDING'
);

CREATE INDEX IF NOT EXISTS idx_predictions_node ON ai_predictions(node_id);
CREATE INDEX IF NOT EXISTS idx_predictions_created ON ai_predictions(created_at DESC);

-- -----------------------------------------------------------------
-- 10. GATEWAY (Raspberry Pi main box edge status)
-- -----------------------------------------------------------------
CREATE TABLE IF NOT EXISTS gateway (
  id                 SERIAL PRIMARY KEY,
  name               VARCHAR(128) DEFAULT 'Raspberry Pi Main Box',
  device_id          VARCHAR(64) UNIQUE NOT NULL DEFAULT 'RPI-GW-01',
  ip_address         VARCHAR(64),
  status             VARCHAR(16) DEFAULT 'ONLINE', -- ONLINE, DEGRADED, OFFLINE
  cpu_usage          FLOAT DEFAULT 0.0,
  ram_usage          FLOAT DEFAULT 0.0,
  temperature        FLOAT DEFAULT 42.0,
  storage_used       FLOAT DEFAULT 0.0,
  mqtt_status        VARCHAR(16) DEFAULT 'ONLINE',
  mesh_status        VARCHAR(16) DEFAULT 'ONLINE',
  db_status          VARCHAR(16) DEFAULT 'ONLINE',
  internet_connected BOOLEAN DEFAULT FALSE,
  cloud_sync_status  VARCHAR(16) DEFAULT 'IDLE',   -- IDLE, SYNCING, SYNCED, ERROR
  alarm_active       BOOLEAN DEFAULT FALSE,
  last_seen          TIMESTAMPTZ DEFAULT NOW(),
  updated_at         TIMESTAMPTZ DEFAULT NOW()
);

-- -----------------------------------------------------------------
-- 11. GATEWAY EVENTS (Edge state transitions and alerts)
-- -----------------------------------------------------------------
CREATE TABLE IF NOT EXISTS gateway_events (
  id          SERIAL PRIMARY KEY,
  event_type  VARCHAR(64) NOT NULL, -- BOOT, INTERNET_LOST, INTERNET_RESTORED, ALARM_TRIGGERED, ALARM_SILENCED, SYNC_COMPLETE
  description TEXT,
  metadata    JSONB,
  created_at  TIMESTAMPTZ DEFAULT NOW(),
  sync_status VARCHAR(16) DEFAULT 'PENDING'
);

-- -----------------------------------------------------------------
-- 12. NOTIFICATION QUEUE (Offline buffered SMS & Email alerts)
-- -----------------------------------------------------------------
CREATE TABLE IF NOT EXISTS notification_queue (
  id           SERIAL PRIMARY KEY,
  alert_id     INTEGER REFERENCES alerts(id) ON DELETE CASCADE,
  type         VARCHAR(16) NOT NULL, -- EMAIL, SMS, PUSH
  recipient    VARCHAR(256) NOT NULL,
  subject      VARCHAR(512),
  body         TEXT,
  status       VARCHAR(16) DEFAULT 'PENDING', -- PENDING, SYNCING, SENT, FAILED
  retry_count  INTEGER DEFAULT 0,
  last_attempt TIMESTAMPTZ,
  sent_at      TIMESTAMPTZ,
  created_at   TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_notif_status ON notification_queue(status);

-- -----------------------------------------------------------------
-- 13. SYNC QUEUE (Offline data to cloud sync buffer)
-- -----------------------------------------------------------------
CREATE TABLE IF NOT EXISTS sync_queue (
  id           SERIAL PRIMARY KEY,
  table_name   VARCHAR(64) NOT NULL,
  record_id    INTEGER NOT NULL,
  operation    VARCHAR(16) NOT NULL, -- INSERT, UPDATE, DELETE
  payload      JSONB,
  status       VARCHAR(16) DEFAULT 'PENDING', -- PENDING, SYNCING, SYNCED, FAILED
  retry_count  INTEGER DEFAULT 0,
  last_attempt TIMESTAMPTZ,
  created_at   TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_sync_status ON sync_queue(status);

-- -----------------------------------------------------------------
-- 14. RESPONSIBLE PERSONS (Role-based access & duty roster)
-- -----------------------------------------------------------------
CREATE TABLE IF NOT EXISTS responsible_persons (
  id           SERIAL PRIMARY KEY,
  firebase_uid VARCHAR(128) UNIQUE NOT NULL,
  email        VARCHAR(256) UNIQUE NOT NULL,
  name         VARCHAR(256),
  role         VARCHAR(32) NOT NULL DEFAULT 'OPERATOR', -- ADMIN, OPERATOR, SAFETY_OFFICER, VIEWER
  phone        VARCHAR(32),
  is_active    BOOLEAN DEFAULT TRUE,
  created_at   TIMESTAMPTZ DEFAULT NOW(),
  updated_at   TIMESTAMPTZ DEFAULT NOW()
);

-- -----------------------------------------------------------------
-- 15. NODE CONNECTIVITY EVENTS (Route changes & dynamic mesh logs)
-- -----------------------------------------------------------------
CREATE TABLE IF NOT EXISTS node_connectivity_events (
  id             SERIAL PRIMARY KEY,
  node_id        INTEGER REFERENCES nodes(id) ON DELETE CASCADE NOT NULL,
  event_type     VARCHAR(32) NOT NULL, -- CONNECTED, DISCONNECTED, RECONNECTED, ROUTE_CHANGED
  old_route      JSONB,
  new_route      JSONB,
  hop_count      INTEGER,
  parent_node_id INTEGER REFERENCES nodes(id) ON DELETE SET NULL,
  occurred_at    TIMESTAMPTZ DEFAULT NOW(),
  sync_status    VARCHAR(16) DEFAULT 'PENDING'
);

CREATE INDEX IF NOT EXISTS idx_conn_events_node ON node_connectivity_events(node_id);
CREATE INDEX IF NOT EXISTS idx_conn_events_time ON node_connectivity_events(occurred_at DESC);

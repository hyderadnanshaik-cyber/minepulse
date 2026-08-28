# Database Architecture & Migration Guide

## Overview
The RED HACK Mine Subsidence Monitoring System uses **PostgreSQL 16/18 with PostGIS** extensions for spatial-temporal telemetry, mesh topology modeling, and real-time risk assessment. In edge deployments (Raspberry Pi gateway / offline nodes), a local SQLite/PostgreSQL buffer is utilized and synchronized when connectivity is restored.

---

## Schema Structure
The schema is defined in [schema.sql](file:///c:/Users/sabih/OneDrive/Desktop/MinorSafetySIH2026/database/schema.sql) and consists of 15 core tables:

1. `panels`: Geographic working panels/mine sections with polygonal geometry.
2. `nodes`: ESP32 sensor node metadata, current status, coordinates, battery, risk scores, and parent-child mesh relationships.
3. `node_registration_codes`: 6-digit security pairing codes for seamless hardware provisioning.
4. `sensor_readings`: High-throughput time-series sensor telemetry (tilt, displacement, vibration, crack, temp, battery, signal).
5. `crack_events`: Dedicated crack detection timeline and spatial incidents.
6. `mesh_connections`: Directed mesh topology links between neighboring nodes with hop counts and RSSI.
7. `alerts`: Subsidence and anomaly alert events with spatial impact polygons and risk severity.
8. `alert_actions`: Audit trail for operator acknowledgments, evacuations, and mitigation notes.
9. `ai_predictions`: Isolation Forest and heuristic anomaly scores, risk evaluations, and confidence metrics.
10. `gateway`: Hardware status, CPU/RAM/temperature metrics, and connectivity health of edge gateway.
11. `gateway_events`: Edge state transitions, alarm activations, and failover event logging.
12. `notification_queue`: Outbox buffer for SMS and email alerts with retry management.
13. `sync_queue`: Bidirectional change-data-capture queue for edge-to-cloud synchronization.
14. `responsible_persons`: Role-based access control and contact information linked to Firebase Auth UIDs.
15. `node_connectivity_events`: Dynamic routing change logs and parent switch events.

---

## Initializing the Database

### Method 1: Docker Compose (Automated)
When starting with Docker Compose, `schema.sql` and `seed.sql` are automatically executed on first container initialization:
```bash
docker compose up -d postgres
```

### Method 2: Manual PostgreSQL Initialization
```bash
# Connect to PostgreSQL
psql -U postgres -h localhost -d postgres

# Create database
CREATE DATABASE mine_monitoring;
\c mine_monitoring

# Apply PostGIS extension and schema
\i database/schema.sql

# Seed development data
\i database/seed.sql
```

---

## Alembic Migrations (FastAPI Backend)

Database migrations in the backend are managed via Alembic.

### Running Migrations:
```bash
cd backend
alembic upgrade head
```

### Creating New Migration:
```bash
alembic revision --autogenerate -m "add_column_to_nodes"
```

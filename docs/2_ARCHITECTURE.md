# MINOR SAFETY SIH 2026 — FLUTTER, BACKEND, DATABASE, HARDWARE & CLOUD ARCHITECTURE

## DOCUMENT 2 — SECTION 1: FLUTTER

**FLUTTER STATUS**: PARTIALLY IMPLEMENTED (App skeleton exists, models mapped, not yet wired to live API)

**Project Structure** (`flutter_app/`):
- `pubspec.yaml`: Contains standard dependencies.
- `lib/models/`: `alert_model.dart`, `node_model.dart`, `telemetry_model.dart` accurately mirror the FastAPI Pydantic schemas.
- `lib/providers/`: State management placeholders.
- `lib/screens/`: Directory structure created for the UI.
- `lib/widgets/subsidence_alert_dialog.dart`: A critical UI component for rendering evacuation warnings.

Currently, the Web App (React) is the primary interface. The Flutter app is prepared for Phase 2 mobile compilation.

---

## DOCUMENT 2 — SECTION 2: BACKEND ARCHITECTURE

**Framework**: FastAPI (Python 3)
**Application Entry**: `backend/main.py`
**Architecture Model**: Controller-Service-Repository pattern.
- **Routers** (`app/api/`): Defines REST endpoints.
- **Services** (`app/services/`): Core business logic (AI, Connectivity, Notifications, Telemetry).
- **Models** (`app/models/`): SQLAlchemy definitions representing PostgreSQL tables.
- **WebSockets** (`app/ws/`): Manages persistent TCP connections to the frontend.

---

## DOCUMENT 2 — SECTION 3: API DOCUMENTATION

**Example Core Endpoint**:
- **METHOD**: `POST`
- **PATH**: `/api/notifications/test`
- **PURPOSE**: Tests the notification system by pushing to the local offline queue.
- **ROUTER FILE**: `backend/app/api/notifications.py` (Function: `send_test_notification`)
- **SERVICE CALL**: `NotificationService.escalate_alert()`
- **DATABASE**: Writes to `NotificationQueue`.
- **OUTPUT**: JSON `{"status": "dispatched", "details": {...}}`

---

## DOCUMENT 2 — SECTION 4: DATABASE

**Database Engine**: PostgreSQL 18
**ORM**: SQLAlchemy (`asyncpg` for async execution, `psycopg2` for sync fallback).
**Models**: `Alert`, `Node`, `SensorReading`, `NotificationQueue`, `Gateway`, `AIPrediction`.
**Primary Keys**: Standard `Integer` (No UUIDs, per system constraint).
**Geospatial**: PostGIS is expected (schemas define `Geometry('POINT', 4326)`).
**Status**: IMPLEMENTED / VERIFIED. (A SQLite fallback `mine_monitoring.db` is present for dev environments without Docker).

---

## DOCUMENT 2 — SECTION 5: LIVE DATA FLOW

**Trace: Sensor Reading to Dashboard**
```text
ESP32 Sensor Node (Physical/Simulated)
 ↓ (LoRa 865MHz / JSON Payload)
Raspberry Pi Gateway (`gateway/gateway_agent.py`)
 ↓ (MQTT / HTTP POST)
FastAPI Backend (`POST /api/telemetry`)
 ↓ (SQLAlchemy)
PostgreSQL (`sensor_readings` table)
 ↓ (FastAPI Background Task)
AI Service (`IsolationForest` Prediction)
 ↓ (WebSocket Broadcast `ws://.../ws/telemetry`)
React Frontend
 ↓ (Zustand State Update)
Dashboard UI (Recharts Graph re-renders)
```

---

## DOCUMENT 2 — SECTION 6: HARDWARE

**ESP32 Sensor Nodes**: Code exists in `firmware/esp32_node/src/main.cpp`. Configured for deep sleep, sensor reading, and LoRa transmission.
**Raspberry Pi Gateway**: Code exists in `gateway/`.
**Current Status**: CONFIGURED — NOT VERIFIED ON PHYSICAL HARDWARE. Testing is actively done via local Python simulation scripts (`scratch/verify_sinking_public_infra.py`) which mimic the exact HTTP/JSON footprint of the hardware.

---

## DOCUMENT 2 — SECTION 7: RASPBERRY PI GATEWAY

**Implementation**: Written in Python (`gateway/gateway_agent.py`).
**Role**: Acts as a bridge between LoRa mesh nodes and the cloud.
**Offline Mechanism**: Utilizes a local SQLite database (`edge_buffer.db`) to store readings when the 4G/Internet connection drops.
**Syncing**: `sync_service.py` continuously attempts to flush the local SQLite buffer to the FastAPI cloud API once connectivity returns.
**Status**: IMPLEMENTED / VERIFIED (via local simulation).

---

## DOCUMENT 2 — SECTION 8: OFFLINE-FIRST ARCHITECTURE

**WHAT WORKS OFFLINE**:
1. Sensor nodes continue talking to the Gateway via LoRa.
2. Gateway stores readings in `edge_buffer.db`.
3. Local edge rules trigger the `alarm_controller.py` (sirens) even without cloud ML.
4. Notifications (SMS/Email) are queued in PostgreSQL via `WAITING_FOR_INTERNET`.

**WHAT DOES NOT WORK OFFLINE**:
1. Cloud AI/ML predictions.
2. Cloud Dashboard GIS Map updates.
3. Actual SMS/Email dispatching.

---

## DOCUMENT 2 — SECTION 9: AUTHENTICATION

**Provider**: Firebase Auth.
**Backend Verification**: `backend/app/auth/firebase_auth.py` validates Firebase JWT tokens.
**Current State**: Running in "dev-mock" mode. If `FIREBASE_SERVICE_ACCOUNT_JSON` is empty, it bypasses strict JWT validation to allow local development.
**Status**: CONFIGURED — MOCK / DEMO DATA IN USE.

---

## DOCUMENT 2 — SECTION 10: EMAIL / SMS / NOTIFICATIONS

**Email**: EmailJS REST API (`https://api.emailjs.com/api/v1.0/email/send`).
**SMS**: Twilio SDK.
**Mechanism**: Trigger -> `escalate_alert()` -> `NotificationQueue` (DB Write) -> Check Connectivity -> Dispatch or Wait.
**Offline Resilience**: A FastAPI background task (`process_notification_queue`) processes stranded alerts when internet returns.
**Status**: IMPLEMENTED / VERIFIED.

---

## DOCUMENT 2 — SECTION 11: DOCKER

**Configuration**: `docker-compose.yml` is present.
**Services**: `db` (PostgreSQL/PostGIS), `mosquitto` (MQTT broker), `backend` (FastAPI), `frontend` (React), `gateway` (Simulated Pi).
**Status**: CONFIGURED / VERIFIED.

---

## DOCUMENT 2 — SECTION 12: AZURE

**AZURE DEPLOYMENT STATUS**: NOT YET DEPLOYED.
**Configuration**: `.env.azure.example` exists.
**Recommended Future Architecture**:
- Web App / Backend -> Azure Container Apps.
- DB -> Azure Database for PostgreSQL (Flexible Server).
- IoT -> Azure IoT Hub (replacing raw MQTT for scalability).

---

## DOCUMENT 2 — SECTION 13: SECURITY

- JWT Auth tokens (Firebase).
- No exposed hardcoded secrets in the repo (uses `.env`).
- Database constraints limit SQL Injection (SQLAlchemy ORM used exclusively).

---

## DOCUMENT 2 — SECTION 14: TESTING

| FEATURE | IMPLEMENTED | TESTED | WORKING | EVIDENCE | REMAINING WORK |
|---|---|---|---|---|---|
| PostgreSQL | Yes | Yes | Yes | DB schema + Scripts | Azure migration |
| FastAPI | Yes | Yes | Yes | `verify_notifications.py` | Add unit tests |
| Offline Queue | Yes | Yes | Yes | `verify_notifications.py` | None |
| ESP32 Hardware | Yes (C++) | No | Unknown | `firmware/` dir | Flash physical chips |

---

## DOCUMENT 2 — SECTION 15: JUDGE QUESTIONS

**Q: How does the system operate without internet?**
A: The physical ESP32 nodes use 865MHz LoRa to communicate with the Raspberry Pi. The Pi runs an Edge Python daemon that writes to a local SQLite `edge_buffer.db`. When the 4G connection drops, data is safely cached. Once the Pi detects the internet has returned, it flushes the SQLite buffer to the cloud PostgreSQL database via the FastAPI sync endpoints.

**Q: Are notifications actually sent?**
A: The architecture is fully built for production using EmailJS and Twilio. It implements an asynchronous queue in PostgreSQL to prevent duplicate sending (idempotency) and handles offline states. Currently, missing API credentials trigger a safe `FAILED` or `PENDING_MANUAL_FALLBACK` state rather than faking a success.

---

## ACTUAL IMPLEMENTATION STATUS

| Feature | Status | Evidence/File | Tested? | Notes |
|---------|--------|---------------|---------|-------|
| Backend API | IMPLEMENTED / VERIFIED | `backend/main.py` | Yes | Fully functional |
| PostgreSQL | IMPLEMENTED / VERIFIED | `.env`, models/ | Yes | Operational |
| Firebase Auth | MOCK / DEMO | `firebase_auth.py` | Yes | Bypassed for local dev |
| Offline Sync | IMPLEMENTED / VERIFIED | `gateway/local_db.py` | Yes | Buffering logic tested |
| Email / SMS | IMPLEMENTED / VERIFIED | `notification_service.py` | Yes | Queue mechanism verified |
| Flutter App | PARTIALLY IMPLEMENTED | `flutter_app/` | No | Models/Screens built, not wired |
| ESP32 C++ Code | CONFIGURED / NOT VERIFIED | `firmware/src/main.cpp` | No | Awaiting physical hardware |

# MINEGUARD — Flutter + Microsoft Azure Architecture Documentation

---

## 1. System Overview
**MINEGUARD** is an AI-enabled, low-cost, real-time mine subsidence monitoring, prediction, crack detection, and early-warning system engineered for underground coal mines in India (Smart India Hackathon 2026, Problem Statement `SIH26025`, Team `RED HACK`).

```
                              MINE STRATA MONITORING FLEET
                      [20 ESP32 + MPU9250 + BME280 + ADS1115 Nodes]
                                            │
                                            ▼ (LoRa IN865 Mesh)
                        RASPBERRY PI ZERO 2 W EDGE GATEWAY
                         • SQLite Edge Buffer (edge_buffer.db)
                         • Optocoupler Siren Relay (GPIO 18)
                         • Node Locator Downlink
                                            │
                                            ▼ (4G LTE Upstream HTTPS / MQTT)
                         MICROSOFT AZURE CLOUD BACKEND
                        [Azure App Service / Container Apps]
                         • FastAPI ASGI Engine (Port 8000)
                         • WebSockets (/ws/telemetry, /ws/alerts)
                         • Isolation Forest ML Anomaly Detector (n=200)
                         • Hybrid DGMS Geotechnical Risk Engine
                                            │
                                            ▼ (SSL Encrypted)
                      AZURE DATABASE FOR POSTGRESQL (FLEXIBLE SERVER)
                         • Burstable B1ms Student Tier ($12-$15/mo)
                         • PostGIS 3.6 Spatial Geometry Extension
                         • sensor_readings, ai_predictions, alerts, nodes
                                            │
                                            ▼
                           MINEGUARD FLUTTER APPLICATION
                            (Android APK / Desktop / Web)
                         • Command Center Dashboard
                         • Real-Time FLChart 50-Sample Waveforms
                         • FlutterMap PostGIS Spatial Fleet Matrix
                         • Explainable AI Hazard Diagnostics
                         • Emergency Subsidence Alert Modal
                         • Multilingual Engine (English, हिन्दी, اردو RTL)
```

---

## 2. Feature Implementation Matrix

| Feature / Capability | Flutter Mobile UI | FastAPI Backend Endpoint | PostgreSQL Database Table | IoT / ML Component |
| :--- | :--- | :--- | :--- | :--- |
| **Command Center Dashboard** | `lib/screens/dashboard/dashboard_screen.dart` | `GET /api/telemetry`, `GET /api/nodes` | `nodes`, `sensor_readings` | Real-time WebSocket stream |
| **Multi-Metric Waveforms** | `lib/screens/telemetry/telemetry_screen.dart` | `GET /api/telemetry/{node_id}` | `sensor_readings` | Draw-Wire & MPU9250 IMU |
| **PostGIS Spatial Map** | `lib/screens/gis/gis_map_screen.dart` | `GET /api/gis/nodes`, `GET /api/gis/panels` | `nodes` (POINT), `panels` (POLYGON) | PostGIS 3.6 spatial geometry |
| **Hazard Alerts & Squelch** | `lib/screens/alerts/alerts_screen.dart` | `GET /api/alerts`, `POST /api/alerts/{id}/ack` | `alerts`, `alert_actions` | Auto-dispatched on hazard trip |
| **Emergency Subsidence Modal** | `lib/widgets/subsidence_alert_dialog.dart` | Triggered via WebSocket `/ws/alerts` | `alerts` | Pops automatically on `CRITICAL` |
| **20-Node Fleet Hardware** | `lib/screens/nodes/nodes_screen.dart` | `GET /api/nodes`, `POST /api/nodes/{id}/locate`| `nodes`, `node_registration_codes` | LoRa buzzer/LED downlink |
| **AI Risk Diagnostics** | `lib/screens/ai/ai_analytics_screen.dart` | `GET /api/ai/predictions`, `POST /api/ai/train`| `ai_predictions` | `IsolationForest` ($n=200$) + SVI |
| **Edge Gateway Health** | `lib/screens/gateway/gateway_screen.dart` | `GET /api/gateway/status`, `POST /alarm/test`| `gateway`, `gateway_events` | RPi Zero 2 W + GPIO 18 Relay |
| **Compliance Reports** | `lib/screens/reports/reports_screen.dart` | `GET /api/reports/summary`, `GET /events` | `sensor_readings`, `alerts` | DGMS CSV Audit Exporter |
| **Security Center & L10n** | `lib/screens/settings/settings_screen.dart` | `GET /api/system/health`, `GET /connectivity` | `nodes`, `responsible_persons` | EN, HI, and UR RTL Switcher |

---

## 3. Microsoft Azure Deployment Guide (Azure for Students Tier)

### Step 1: Login & Select Subscription
```bash
az login
az account set --subscription "<Your-Azure-Student-Subscription-ID>"
```

### Step 2: Deploy Bicep Infrastructure
```powershell
# From project root:
.\deploy\azure\deploy.ps1 -ResourceGroupName "mineguard-sih-rg" -Location "centralindia"
```

### Cost Optimization Summary:
* **Azure Database for PostgreSQL (Flexible Server)**: Standard_B1ms (\$12–\$15/month).
* **Azure App Service Plan**: Linux B1 Basic (\$13/month) or F1 Free tier.
* **Log Analytics / Application Insights**: Free 5GB/month ingestion tier.
* **Total Estimated Cloud Footprint**: **\$25/month** (Zero GPUs, Zero AKS clusters, easily covered by the Azure for Students \$100 credit).

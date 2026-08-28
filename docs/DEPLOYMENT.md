# RED HACK Deployment & Operations Guide

## 1. Deployment Topologies

The system supports three primary deployment configurations:
1. **Local Development / Evaluation Environment** (Single machine with simulator)
2. **Autonomous Edge Gateway** (Raspberry Pi on-site appliance with offline local UI)
3. **Cloud Production Platform** (Scalable central cloud with PostGIS & multi-mine dashboard)

---

## 2. Option A: Local Development Deployment

### 2.1 Clone & Environment Setup
```bash
git clone <repo_url> MinorSafetySIH2026
cd MinorSafetySIH2026
cp .env.example .env
```

### 2.2 Run with Docker Compose (Recommended)
```bash
# Launch PostgreSQL + PostGIS, Mosquitto Broker, FastAPI Backend, ML Worker
docker compose up -d

# Check running status
docker compose ps

# (Optional) Launch with 20-Node Sensor Simulator
docker compose --profile simulation up -d
```

### 2.3 Run Frontend Locally
```bash
cd frontend
npm install
npm run dev
# Dashboard available at http://localhost:5173
```

---

## 3. Option B: Raspberry Pi Edge Gateway Deployment

### 3.1 OS & Prerequisite Packages
Install Raspberry Pi OS 64-bit Lite on an SD card or NVMe SSD:
```bash
sudo apt update && sudo apt upgrade -y
sudo apt install -y python3-pip python3-venv mosquitto mosquitto-clients \
  nginx git libpq-dev postgresql postgresql-contrib postgis
```

### 3.2 Mosquitto Broker Setup
Copy configuration to Mosquitto:
```bash
sudo cp mosquitto/mosquitto.conf /etc/mosquitto/conf.d/redhack.conf
sudo systemctl restart mosquitto
sudo systemctl enable mosquitto
```

### 3.3 Backend Systemd Daemon
Create a systemd unit file `/etc/systemd/system/redhack-backend.service`:
```ini
[Unit]
Description=RED HACK FastAPI Edge Service
After=network.target mosquitto.service postgresql.service

[Service]
User=pi
WorkingDirectory=/home/pi/MinorSafetySIH2026/backend
ExecStart=/home/pi/MinorSafetySIH2026/backend/.venv/bin/uvicorn main:app --host 0.0.0.0 --port 8000
Restart=always
RestartSec=5
EnvironmentFile=/home/pi/MinorSafetySIH2026/.env

[Install]
WantedBy=multi-user.target
```

Enable and start service:
```bash
sudo systemctl daemon-reload
sudo systemctl enable redhack-backend
sudo systemctl start redhack-backend
```

### 3.4 WiFi Access Point (`MineNet-Emergency`)
Configure `hostapd` and `dnsmasq` so tablets and safety personnel can connect directly to `192.168.4.1` underground without any external router.

---

## 4. Option C: Cloud Platform & Frontend Vercel Deployment

### 4.1 Frontend on Vercel
1. Link your GitHub repository to Vercel.
2. Set Root Directory to `frontend`.
3. Configure Build Command: `npm run build` and Output Directory: `dist`.
4. Configure Environment Variables in Vercel Dashboard:
   - `VITE_FIREBASE_API_KEY`
   - `VITE_FIREBASE_AUTH_DOMAIN`
   - `VITE_FIREBASE_PROJECT_ID`
   - `VITE_API_BASE_URL` (URL of your Cloud FastAPI instance)
   - `VITE_WS_BASE_URL` (WebSocket URL of your Cloud FastAPI instance)

### 4.2 Cloud Backend Deployment (Docker / Linux VM)
```bash
docker compose -f docker-compose.yml up -d --build
```

---

## 5. Environment Variables Reference

| Variable | Default / Example | Required In | Purpose |
| :--- | :--- | :---: | :--- |
| `DATABASE_URL` | `postgresql+asyncpg://postgres:pass@localhost:5432/mine_monitoring` | Backend | Async database connection string |
| `MQTT_BROKER_HOST` | `localhost` / `mosquitto` | Backend, Simulator | MQTT broker hostname |
| `MQTT_BROKER_PORT` | `1883` | Backend, Simulator | MQTT broker TCP port |
| `ALARM_GPIO_PIN` | `18` | Edge Pi | Raspberry Pi BCM Pin for Siren Relay |
| `VITE_API_BASE_URL` | `http://localhost:8000` | Frontend | REST API base endpoint |
| `VITE_WS_BASE_URL` | `ws://localhost:8000` | Frontend | WebSocket real-time stream endpoint |
| `VITE_GATEWAY_LOCAL_URL` | `http://192.168.4.1:8000` | Frontend | Fallback edge gateway IP for offline mode |

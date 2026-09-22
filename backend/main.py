import os
import sys

# Ensure root workspace is in sys.path
sys.path.insert(0, os.path.abspath(".."))
sys.path.insert(0, os.path.abspath("."))

import logging
import asyncio
from datetime import datetime
from contextlib import asynccontextmanager
from fastapi import FastAPI, WebSocket, WebSocketDisconnect, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import select

from app.core.config import settings
from app.core.database import async_engine, AsyncSessionLocal
from app.models import Panel, Node, NodeRegistrationCode, Gateway
from app.models.infrastructure import InfrastructureAsset, MineConfig
from app.api import nodes, telemetry, alerts, ai, gis, mesh, gateway, system, sync, reports, simulation, notifications
from app.api import infrastructure as infrastructure_api
from app.ws.manager import ws_manager
from app.mqtt.client import mqtt_client

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(name)s: %(message)s")
logger = logging.getLogger("mineguard.main")

async def verify_and_seed_postgres():
    """Ensures Panel Alpha, 20 MINEGUARD nodes, Gateway, MineConfig, and Infrastructure exist in PostgreSQL."""
    try:
        async with AsyncSessionLocal() as db:
            # 1. Check Panel
            p_res = await db.execute(select(Panel).filter_by(panel_id="PANEL-A"))
            panel = p_res.scalar_one_or_none()
            if not panel:
                panel = Panel(
                    panel_id="PANEL-A",
                    name="Panel Alpha North",
                    description="Primary working panel for SIH2026 MINEGUARD",
                    status="ACTIVE"
                )
                db.add(panel)
                await db.commit()

            # 2. Check and provision NODE_01 to NODE_20
            # These nodes are placed around the authoritative Jharia mine site (23.7692838, 86.4110045)
            # Distributed in a realistic underground grid pattern ±350m around mine entrance
            now = datetime.now()
            node_offsets = [
                # (lat_offset_deg, lon_offset_deg) — arranged as realistic underground sensor grid
                (-0.0008, -0.0012), (-0.0008, -0.0006), (-0.0008, 0.0000), (-0.0008, 0.0006), (-0.0008, 0.0012),
                (-0.0004, -0.0012), (-0.0004, -0.0006), (-0.0004, 0.0000), (-0.0004, 0.0006), (-0.0004, 0.0012),
                (-0.0000, -0.0012), (-0.0000, -0.0006), (-0.0000, 0.0000), (-0.0000, 0.0006), (-0.0000, 0.0012),
                ( 0.0004, -0.0012), ( 0.0004, -0.0006), ( 0.0004, 0.0000), ( 0.0004, 0.0006), ( 0.0004, 0.0012),
            ]
            BASE_LAT = 23.7692838
            BASE_LON = 86.4110045
            for i in range(1, 21):
                code = f"NODE_{i:02d}"
                dlat, dlon = node_offsets[i - 1]
                target_lat = BASE_LAT + dlat
                target_lon = BASE_LON + dlon
                n_res = await db.execute(select(Node).filter_by(node_id=code))
                node = n_res.scalar_one_or_none()
                if not node:
                    node = Node(
                        node_id=code,
                        panel_id_fk="PANEL-A",
                        latitude=target_lat,
                        longitude=target_lon,
                        status="ONLINE",
                        battery_level=94.0 - (i * 0.4),
                        installed_at=now
                    )
                    db.add(node)
                    reg_code = NodeRegistrationCode(
                        code=f"{100000 + i:06d}",
                        node_id=code,
                        status="USED",
                        created_at=now,
                        used_at=now
                    )
                    db.add(reg_code)
                elif node.latitude is None or abs(node.latitude - BASE_LAT) > 0.005:
                    node.latitude = target_lat
                    node.longitude = target_lon

            # 3. Check Gateway — explicitly place at surface operations (near mine entrance)
            gw_res = await db.execute(select(Gateway).filter_by(device_id="RPI-ZERO2W-001"))
            gw = gw_res.scalar_one_or_none()
            if not gw:
                gw = Gateway(
                    name="Main Gateway — Raspberry Pi",
                    device_id="RPI-ZERO2W-001",
                    ip_address="127.0.0.1",
                    latitude=23.7698000,   # Surface operations — ~60m north of mine entrance
                    longitude=86.4108500,
                    status="ONLINE",
                    cpu_usage=18.5,
                    ram_usage=34.2,
                    temperature=41.2,
                    storage_used=35.0,
                    mqtt_status="ONLINE",
                    mesh_status="ONLINE",
                    db_status="ONLINE",
                    internet_connected=True,
                    cloud_sync_status="SYNCED",
                    alarm_active=False,
                    last_seen=now
                )
                db.add(gw)
            elif gw.latitude is None:
                # Update existing gateway with GPS coordinates if missing
                gw.latitude = 23.7698000
                gw.longitude = 86.4108500
                gw.name = "Main Gateway — Raspberry Pi"

            await db.commit()

            # 4. Seed Authoritative Mine Site Config (Jharia Coalfield — exact Google Maps coordinate)
            mine_configs = [
                ("MINE_SITE_LAT",  "23.7692838",   "Authoritative Jharia Coal Mine latitude (WGS84). Source: Google Maps."),
                ("MINE_SITE_LON",  "86.4110045",   "Authoritative Jharia Coal Mine longitude (WGS84). Source: Google Maps."),
                ("MINE_SITE_NAME", "Jharia Coalfield — MINEGUARD Mine Site", "Official mine site display name."),
            ]
            for key, value, desc in mine_configs:
                existing = await db.execute(select(MineConfig).filter_by(key=key))
                if not existing.scalar_one_or_none():
                    db.add(MineConfig(key=key, value=value, description=desc))
            await db.commit()

            # 5. Seed Mine Infrastructure Assets (only if table is empty)
            infra_count = await db.execute(select(InfrastructureAsset))
            existing_infra = infra_count.scalars().all()
            if not existing_infra:
                # Infrastructure assets are placed at realistic offsets from the Jharia mine site.
                # These represent typical Jharia coalfield surface and underground infrastructure.
                infrastructure_seed = [
                    {
                        "name": "Main Mine Entrance & Winding House",
                        "asset_type": "MAIN_ENTRANCE",
                        "latitude": BASE_LAT + 0.0006,   # ~67m north of site
                        "longitude": BASE_LON - 0.0002,
                        "criticality": "CRITICAL",
                        "status": "OPERATIONAL",
                        "description": "Primary access portal and haulage winding station.",
                    },
                    {
                        "name": "Underground Main Haulage Tunnel",
                        "asset_type": "TUNNEL",
                        "latitude": BASE_LAT - 0.0002,   # ~22m south (underground entry)
                        "longitude": BASE_LON + 0.0000,
                        "criticality": "CRITICAL",
                        "status": "OPERATIONAL",
                        "description": "Main underground haulage drift connecting all panels.",
                    },
                    {
                        "name": "Ventilation Shaft #1 (Upcast)",
                        "asset_type": "VENTILATION_SYSTEM",
                        "latitude": BASE_LAT + 0.0002,
                        "longitude": BASE_LON + 0.0016,  # ~155m east
                        "criticality": "CRITICAL",
                        "status": "OPERATIONAL",
                        "description": "Primary upcast ventilation shaft. Failure risks gas build-up in all panels.",
                    },
                    {
                        "name": "Surface Control Room & Monitoring Station",
                        "asset_type": "CONTROL_ROOM",
                        "latitude": BASE_LAT + 0.0010,   # ~111m north (surface)
                        "longitude": BASE_LON - 0.0006,
                        "criticality": "HIGH",
                        "status": "OPERATIONAL",
                        "description": "SCADA monitoring, communication relay, and emergency coordination centre.",
                    },
                    {
                        "name": "Electrical Substation Alpha",
                        "asset_type": "ELECTRICAL_SUBSTATION",
                        "latitude": BASE_LAT + 0.0008,
                        "longitude": BASE_LON + 0.0008,  # ~90m northeast
                        "criticality": "HIGH",
                        "status": "OPERATIONAL",
                        "description": "33/11 kV surface substation powering all underground equipment.",
                    },
                    {
                        "name": "Pumping Station (Sump Level -120m)",
                        "asset_type": "PUMPING_STATION",
                        "latitude": BASE_LAT - 0.0006,   # ~67m south (deeper underground)
                        "longitude": BASE_LON - 0.0008,
                        "criticality": "HIGH",
                        "status": "OPERATIONAL",
                        "description": "Primary water dewatering pump station at sump level.",
                    },
                    {
                        "name": "Coal Handling & Storage Area",
                        "asset_type": "STORAGE_AREA",
                        "latitude": BASE_LAT + 0.0012,   # ~133m north (surface stockyard)
                        "longitude": BASE_LON + 0.0003,
                        "criticality": "MEDIUM",
                        "status": "OPERATIONAL",
                        "description": "Surface coal stockpile and preparation yard.",
                    },
                    {
                        "name": "Conveyor Belt Main Drive Station",
                        "asset_type": "CONVEYOR",
                        "latitude": BASE_LAT - 0.0004,
                        "longitude": BASE_LON + 0.0010,  # ~95m east underground
                        "criticality": "MEDIUM",
                        "status": "OPERATIONAL",
                        "description": "Panel-to-surface coal transport conveyor drive and tensioning station.",
                    },
                    {
                        "name": "Emergency Escape Shaft #2 (East)",
                        "asset_type": "EMERGENCY_EXIT",
                        "latitude": BASE_LAT - 0.0008,
                        "longitude": BASE_LON + 0.0018,  # ~170m east
                        "criticality": "CRITICAL",
                        "status": "OPERATIONAL",
                        "description": "Secondary emergency egress shaft. Must remain accessible at all times.",
                    },
                    {
                        "name": "Diesel Fuel Store & Compressor Station",
                        "asset_type": "STORAGE_AREA",
                        "latitude": BASE_LAT + 0.0014,
                        "longitude": BASE_LON - 0.0010,  # ~140m northwest (surface)
                        "criticality": "MEDIUM",
                        "status": "OPERATIONAL",
                        "description": "Diesel storage for underground vehicles and compressed air supply.",
                    },
                ]
                for ia in infrastructure_seed:
                    db.add(InfrastructureAsset(**ia, is_active=True))
                await db.commit()
                logger.info(f"Seeded {len(infrastructure_seed)} infrastructure assets around Jharia mine site.")

            logger.info("PostgreSQL database verified and connected successfully!")
    except Exception as e:
        logger.error(f"PostgreSQL initialization note: {e}", exc_info=True)

async def _auto_escalation_loop():
    """Background task: check for unacknowledged CRITICAL alerts and escalate."""
    from app.services.notification_service import escalate_alert
    from app.api.notifications import get_officer_store
    from app.models.alert import Alert as AlertModel

    await asyncio.sleep(60)  # Wait 60s after boot before first check
    while True:
        try:
            timeout_minutes = get_officer_store().get("alert_timeout_minutes", 5)
            officer = get_officer_store()
            if officer.get("email") or officer.get("phone"):
                async with AsyncSessionLocal() as db:
                    from datetime import timedelta
                    cutoff = datetime.now() - timedelta(minutes=timeout_minutes)
                    result = await db.execute(
                        select(AlertModel).where(
                            AlertModel.severity == "CRITICAL",
                            AlertModel.status.in_(["DETECTED", "ACTIVE"]),
                            AlertModel.detected_at <= cutoff
                        )
                    )
                    unacked = result.scalars().all()
                    for alert in unacked:
                        logger.warning(
                            f"[AUTO-ESCALATION] Alert #{alert.id} unacknowledged "
                            f"for {timeout_minutes}min → escalating to {officer.get('name')}"
                        )
                        await escalate_alert(
                            to_email=officer.get("email") or None,
                            to_phone=officer.get("phone") or None,
                            officer_name=officer.get("name", "Safety Officer"),
                            alert_title=alert.title or "CRITICAL Strata Alert",
                            node_code=str(alert.node_id_fk or "UNKNOWN"),
                            severity=alert.severity,
                            risk_score=float(alert.risk_score or 0),
                            message=alert.message or "Unacknowledged critical alert.",
                            detected_at=str(alert.detected_at),
                            notify_email=officer.get("notify_email", True),
                            notify_sms=officer.get("notify_sms", True),
                        )
        except Exception as e:
            logger.debug(f"[AUTO-ESCALATION] Check cycle error: {e}")
        await asyncio.sleep(60)  # Check every 60 seconds

@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Starting MINEGUARD Backend with PostgreSQL 18 + PostGIS...")
    # 1. Verify PostgreSQL connection and data
    await verify_and_seed_postgres()
    
    # 2. Start MQTT client on running loop
    try:
        loop = asyncio.get_running_loop()
        mqtt_client.start(loop)
        logger.info("MQTT Client connected to Mosquitto on port 1883.")
    except Exception as e:
        logger.warning(f"MQTT client startup note: {e}")

    # 3. Start auto-escalation background task
    escalation_task = asyncio.create_task(_auto_escalation_loop())
    logger.info("Alert auto-escalation scheduler started.")
        
    yield
    
    logger.info("Shutting down MINEGUARD Backend...")
    escalation_task.cancel()
    try:
        await escalation_task
    except asyncio.CancelledError:
        pass
    try:
        mqtt_client.stop()
    except Exception:
        pass

app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    description="AI-Enabled Real-Time Mine Subsidence Monitoring, Prediction and Early Warning System (SIH26025)",
    lifespan=lifespan
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# API Routers
app.include_router(nodes.router, prefix=settings.API_PREFIX)
app.include_router(telemetry.router, prefix=settings.API_PREFIX)
app.include_router(alerts.router, prefix=settings.API_PREFIX)
app.include_router(ai.router, prefix=settings.API_PREFIX)
app.include_router(gis.router, prefix=settings.API_PREFIX)
app.include_router(mesh.router, prefix=settings.API_PREFIX)
app.include_router(gateway.router, prefix=settings.API_PREFIX)
app.include_router(system.router, prefix=settings.API_PREFIX)
app.include_router(sync.router, prefix=settings.API_PREFIX)
app.include_router(reports.router, prefix=settings.API_PREFIX)
app.include_router(simulation.router, prefix=settings.API_PREFIX)
app.include_router(notifications.router, prefix=settings.API_PREFIX)
app.include_router(infrastructure_api.router, prefix=settings.API_PREFIX)

# WebSockets for Real-Time Telemetry & Alerts
@app.websocket("/ws/live")
@app.websocket("/ws/telemetry")
async def websocket_telemetry(websocket: WebSocket):
    await ws_manager.connect(websocket, channel="telemetry")
    try:
        while True:
            await websocket.receive_text()
    except WebSocketDisconnect:
        ws_manager.disconnect(websocket, channel="telemetry")

@app.websocket("/ws/alerts")
async def websocket_alerts(websocket: WebSocket):
    await ws_manager.connect(websocket, channel="alerts")
    try:
        while True:
            await websocket.receive_text()
    except WebSocketDisconnect:
        ws_manager.disconnect(websocket, channel="alerts")

@app.websocket("/ws/mesh")
async def websocket_mesh(websocket: WebSocket):
    await ws_manager.connect(websocket, channel="mesh")
    try:
        while True:
            await websocket.receive_text()
    except WebSocketDisconnect:
        ws_manager.disconnect(websocket, channel="mesh")

@app.websocket("/ws/gateway")
async def websocket_gateway(websocket: WebSocket):
    await ws_manager.connect(websocket, channel="gateway")
    try:
        while True:
            await websocket.receive_text()
    except WebSocketDisconnect:
        ws_manager.disconnect(websocket, channel="gateway")

# Locate frontend/dist directory for unified single-origin deployments
dist_dirs = [
    os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "frontend", "dist"),
    os.path.abspath("frontend/dist"),
    os.path.abspath("../frontend/dist"),
    os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "frontend", "dist"),
]
dist_path = next((d for d in dist_dirs if os.path.exists(d) and os.path.isdir(d)), None)

if dist_path and os.path.exists(os.path.join(dist_path, "assets")):
    app.mount("/assets", StaticFiles(directory=os.path.join(dist_path, "assets")), name="static_assets")

@app.get("/api/system/info")
async def system_info():
    return {
        "system": "MINEGUARD Mine Subsidence Monitoring System",
        "problem": "SIH26025",
        "team": "RED HACK",
        "database": "PostgreSQL 18 + PostGIS",
        "gateway": "MINEGATE (Raspberry Pi Zero 2 W)",
        "field_network": "LoRa 868 MHz",
        "status": "OPERATIONAL",
        "offline_first": True,
        "docs": "/docs"
    }

@app.get("/")
async def root():
    if dist_path:
        index_html = os.path.join(dist_path, "index.html")
        if os.path.isfile(index_html):
            return FileResponse(index_html)
    return {
        "system": "MINEGUARD Mine Subsidence Monitoring System",
        "problem": "SIH26025",
        "team": "RED HACK",
        "status": "OPERATIONAL",
        "docs": "/docs"
    }

@app.get("/{full_path:path}")
async def serve_spa_catchall(full_path: str):
    # Do not intercept API, docs, Swagger, or WS routes
    if full_path.startswith("api") or full_path in ["docs", "redoc", "openapi.json"] or full_path.startswith("ws"):
        raise HTTPException(status_code=404, detail="Not Found")

    if dist_path:
        target = os.path.join(dist_path, full_path)
        if os.path.isfile(target):
            return FileResponse(target)
        index_html = os.path.join(dist_path, "index.html")
        if os.path.isfile(index_html):
            return FileResponse(index_html)

    raise HTTPException(status_code=404, detail="Not Found")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)

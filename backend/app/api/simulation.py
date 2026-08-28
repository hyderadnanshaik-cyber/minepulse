from fastapi import APIRouter, Depends, BackgroundTasks
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database import AsyncSessionLocal
from app.auth.firebase_auth import get_current_user
from app.services.telemetry_service import TelemetryService
from app.schemas.telemetry import TelemetryPayload
import asyncio
import logging

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/simulation", tags=["Simulation"])

# Store active simulation state
_active_sim = {
    "running": False,
    "scenario": None,
    "step": 0,
    "total_steps": 0,
    "results": [],
    "last_updated": None
}

SCENARIOS = {
    "SCENARIO_A_SINGLE_SUBSIDENCE": {
        "name": "Scenario A — Progressive Single-Node Sinking",
        "description": "Station NODE_03 experiences accelerating downward displacement and tilt while neighboring stations remain stable. Verifies localized anomaly classification.",
        "steps": [
            # Frame 0: Baseline normal
            {
                "NODE_01": {"displacement": 0.2, "tilt_x": 0.10, "crack_width": 0.0, "vibration": 0.015, "displacement_rate": 0.01},
                "NODE_02": {"displacement": 0.3, "tilt_x": 0.12, "crack_width": 0.0, "vibration": 0.018, "displacement_rate": 0.02},
                "NODE_03": {"displacement": 0.3, "tilt_x": 0.15, "crack_width": 0.0, "vibration": 0.020, "displacement_rate": 0.02},
                "NODE_04": {"displacement": 0.2, "tilt_x": 0.08, "crack_width": 0.0, "vibration": 0.012, "displacement_rate": 0.01}
            },
            # Frame 1: NODE_03 slight movement
            {
                "NODE_01": {"displacement": 0.2, "tilt_x": 0.10, "crack_width": 0.0, "vibration": 0.015, "displacement_rate": 0.01},
                "NODE_02": {"displacement": 0.3, "tilt_x": 0.12, "crack_width": 0.0, "vibration": 0.018, "displacement_rate": 0.02},
                "NODE_03": {"displacement": 4.2, "tilt_x": 0.60, "crack_width": 0.2, "vibration": 0.050, "displacement_rate": 1.20},
                "NODE_04": {"displacement": 0.2, "tilt_x": 0.08, "crack_width": 0.0, "vibration": 0.012, "displacement_rate": 0.01}
            },
            # Frame 2: NODE_03 WATCH threshold breached
            {
                "NODE_01": {"displacement": 0.2, "tilt_x": 0.10, "crack_width": 0.0, "vibration": 0.015, "displacement_rate": 0.01},
                "NODE_02": {"displacement": 0.3, "tilt_x": 0.12, "crack_width": 0.0, "vibration": 0.018, "displacement_rate": 0.02},
                "NODE_03": {"displacement": 12.8, "tilt_x": 1.90, "crack_width": 0.8, "vibration": 0.120, "displacement_rate": 3.80},
                "NODE_04": {"displacement": 0.2, "tilt_x": 0.08, "crack_width": 0.0, "vibration": 0.012, "displacement_rate": 0.01}
            },
            # Frame 3: NODE_03 CRITICAL limit exceeded
            {
                "NODE_01": {"displacement": 0.2, "tilt_x": 0.10, "crack_width": 0.0, "vibration": 0.015, "displacement_rate": 0.01},
                "NODE_02": {"displacement": 0.4, "tilt_x": 0.14, "crack_width": 0.0, "vibration": 0.019, "displacement_rate": 0.03},
                "NODE_03": {"displacement": 29.5, "tilt_x": 4.80, "crack_width": 3.4, "vibration": 0.520, "displacement_rate": 14.50},
                "NODE_04": {"displacement": 0.2, "tilt_x": 0.08, "crack_width": 0.0, "vibration": 0.012, "displacement_rate": 0.01}
            }
        ]
    },
    "SCENARIO_B_CORRELATED_PROPAGATION": {
        "name": "Scenario B — Multi-Node Correlated Propagation",
        "description": "Station NODE_03 begins sinking; shortly afterward, neighboring Station NODE_02 begins showing correlated downward motion and tilt. Verifies multi-node propagation detection, impact polygon calculation, and evacuation recommendation.",
        "steps": [
            # Frame 0: Baseline stable
            {
                "NODE_01": {"displacement": 0.2, "tilt_x": 0.10, "crack_width": 0.0, "vibration": 0.015, "displacement_rate": 0.01},
                "NODE_02": {"displacement": 0.3, "tilt_x": 0.12, "crack_width": 0.0, "vibration": 0.018, "displacement_rate": 0.02},
                "NODE_03": {"displacement": 0.3, "tilt_x": 0.15, "crack_width": 0.0, "vibration": 0.020, "displacement_rate": 0.02},
                "NODE_04": {"displacement": 0.2, "tilt_x": 0.08, "crack_width": 0.0, "vibration": 0.012, "displacement_rate": 0.01}
            },
            # Frame 1: NODE_03 initiates movement
            {
                "NODE_01": {"displacement": 0.2, "tilt_x": 0.10, "crack_width": 0.0, "vibration": 0.015, "displacement_rate": 0.01},
                "NODE_02": {"displacement": 0.3, "tilt_x": 0.12, "crack_width": 0.0, "vibration": 0.018, "displacement_rate": 0.02},
                "NODE_03": {"displacement": 6.5, "tilt_x": 0.90, "crack_width": 0.3, "vibration": 0.080, "displacement_rate": 2.10},
                "NODE_04": {"displacement": 0.2, "tilt_x": 0.08, "crack_width": 0.0, "vibration": 0.012, "displacement_rate": 0.01}
            },
            # Frame 2: NODE_03 accelerates, NODE_02 begins correlated tilt and displacement
            {
                "NODE_01": {"displacement": 0.2, "tilt_x": 0.10, "crack_width": 0.0, "vibration": 0.015, "displacement_rate": 0.01},
                "NODE_02": {"displacement": 4.8, "tilt_x": 0.85, "crack_width": 0.2, "vibration": 0.070, "displacement_rate": 1.40},
                "NODE_03": {"displacement": 18.2, "tilt_x": 2.80, "crack_width": 1.6, "vibration": 0.250, "displacement_rate": 6.50},
                "NODE_04": {"displacement": 0.3, "tilt_x": 0.09, "crack_width": 0.0, "vibration": 0.015, "displacement_rate": 0.02}
            },
            # Frame 3: Multi-node propagation confirmed -> Evacuation advisory
            {
                "NODE_01": {"displacement": 0.3, "tilt_x": 0.11, "crack_width": 0.0, "vibration": 0.018, "displacement_rate": 0.02},
                "NODE_02": {"displacement": 11.5, "tilt_x": 2.10, "crack_width": 0.9, "vibration": 0.180, "displacement_rate": 4.20},
                "NODE_03": {"displacement": 34.0, "tilt_x": 5.50, "crack_width": 3.8, "vibration": 0.680, "displacement_rate": 18.00},
                "NODE_04": {"displacement": 0.3, "tilt_x": 0.10, "crack_width": 0.0, "vibration": 0.016, "displacement_rate": 0.02}
            }
        ]
    },
    "SCENARIO_C_LOCALIZED_CRACK": {
        "name": "Scenario C — Localized Crack Opening",
        "description": "Station NODE_04 develops a localized fissure opening with normal tilt/displacement elsewhere in the fleet.",
        "steps": [
            {
                "NODE_01": {"displacement": 0.2, "tilt_x": 0.10, "crack_width": 0.0, "vibration": 0.015, "displacement_rate": 0.01},
                "NODE_02": {"displacement": 0.3, "tilt_x": 0.12, "crack_width": 0.0, "vibration": 0.018, "displacement_rate": 0.02},
                "NODE_03": {"displacement": 0.3, "tilt_x": 0.15, "crack_width": 0.0, "vibration": 0.020, "displacement_rate": 0.02},
                "NODE_04": {"displacement": 0.2, "tilt_x": 0.08, "crack_width": 3.2, "vibration": 0.030, "displacement_rate": 0.05}
            }
        ]
    },
    "SCENARIO_D_NORMAL_BASELINE": {
        "name": "Scenario D — All Stations Normal Baseline",
        "description": "All 20 monitoring stations stream stable nominal baseline telemetry. Clears active alarms.",
        "steps": [
            {
                "NODE_01": {"displacement": 0.2, "tilt_x": 0.08, "crack_width": 0.0, "vibration": 0.012, "displacement_rate": 0.01},
                "NODE_02": {"displacement": 0.2, "tilt_x": 0.09, "crack_width": 0.0, "vibration": 0.014, "displacement_rate": 0.01},
                "NODE_03": {"displacement": 0.2, "tilt_x": 0.10, "crack_width": 0.0, "vibration": 0.015, "displacement_rate": 0.01},
                "NODE_04": {"displacement": 0.2, "tilt_x": 0.07, "crack_width": 0.0, "vibration": 0.011, "displacement_rate": 0.01}
            }
        ]
    }
}

async def run_simulation(scenario: str, interval_seconds: int):
    global _active_sim
    _active_sim["running"] = True
    _active_sim["scenario"] = scenario
    _active_sim["step"] = 0
    _active_sim["results"] = []

    steps = SCENARIOS.get(scenario, {}).get("steps", [])
    _active_sim["total_steps"] = len(steps)

    try:
        for i, step in enumerate(steps):
            if not _active_sim["running"]:
                break

            _active_sim["step"] = i + 1

            async with AsyncSessionLocal() as db:
                for node_id, data in step.items():
                    payload = TelemetryPayload(
                        node_id=node_id,
                        tilt_x=data.get("tilt_x", 0.0),
                        tilt_y=data.get("tilt_x", 0.0) * 0.4,
                        displacement=data.get("displacement", 0.0),
                        displacement_rate=data.get("displacement_rate", 0.0),
                        vibration=data.get("vibration", 0.0),
                        crack_width=data.get("crack_width", 0.0),
                        crack_detected=data.get("crack_width", 0.0) > 0.5,
                        temperature=25.5,
                        humidity=58.0,
                        pressure=1013.25,
                        battery_level=94.0,
                        rssi=-68.0,
                        hop_count=1
                    )
                    await TelemetryService.process_telemetry(db, payload)

            _active_sim["results"].append({"step": i + 1, "status": "completed"})

            if i < len(steps) - 1:
                await asyncio.sleep(interval_seconds)

    except Exception as e:
        logger.error(f"Simulation error: {e}")
        _active_sim["results"].append({"step": _active_sim["step"], "status": "error", "error": str(e)})
    finally:
        _active_sim["running"] = False

@router.get("/scenarios")
async def list_simulation_scenarios():
    """Returns available simulation scenarios with descriptions and parameters."""
    return [
        {
            "id": k,
            "name": v["name"],
            "description": v["description"],
            "steps_count": len(v["steps"])
        }
        for k, v in SCENARIOS.items()
    ]

@router.post("/start")
async def start_simulation(
    payload: dict,
    background_tasks: BackgroundTasks,
    current_user: dict = Depends(get_current_user)
):
    scenario = payload.get("scenario", "SCENARIO_B_CORRELATED_PROPAGATION")
    interval = payload.get("interval_seconds", 3)

    if _active_sim["running"]:
        return {"status": "error", "message": "Simulation is already running"}

    if scenario not in SCENARIOS:
        # Fallback aliases
        if scenario == "PROGRESSIVE_SINKING":
            scenario = "SCENARIO_A_SINGLE_SUBSIDENCE"
        elif scenario == "NORMAL":
            scenario = "SCENARIO_D_NORMAL_BASELINE"
        else:
            scenario = "SCENARIO_B_CORRELATED_PROPAGATION"

    background_tasks.add_task(run_simulation, scenario, interval)
    return {
        "status": "started",
        "scenario": scenario,
        "name": SCENARIOS.get(scenario, {}).get("name"),
        "interval_seconds": interval,
        "total_steps": len(SCENARIOS.get(scenario, {}).get("steps", []))
    }

@router.get("/status")
async def get_simulation_status(current_user: dict = Depends(get_current_user)):
    return _active_sim

@router.post("/stop")
async def stop_simulation(current_user: dict = Depends(get_current_user)):
    _active_sim["running"] = False
    return {"status": "stopped"}

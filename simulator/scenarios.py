import math
import random
import os
import json
from typing import Dict, Any

class ScenarioManager:
    """
    Physical geotechnical simulator for MINEGUARD 20-node grid.
    Demonstrates SIH 2026 primary test case:
    NODE_03 undergoes progressive inward ground movement, tilt excursion,
    vibration increase, and mechanical crack fissure opening, while surrounding
    stations remain within normal DGMS safety margins.
    """

    def __init__(self):
        self.step_count = 0
        self.mode = "CYCLE"  # "CYCLE", "ANOMALY_NODE_03", "NORMAL"
        self.critical_nodes = {"NODE_03"}
        self.watch_nodes = {"NODE_04", "NODE_14"}

    def set_mode(self, mode: str):
        self.mode = mode

    def mutate_telemetry(self, node_code: str, baseline: Dict[str, Any], step: int) -> Dict[str, Any]:
        self.step_count = step
        result = dict(baseline)

        # Baseline ambient geotechnical micro-variations
        noise_tilt = random.uniform(-0.005, 0.005)
        noise_disp = random.uniform(-0.015, 0.015)
        noise_vib = random.uniform(-0.002, 0.002)
        noise_temp = random.uniform(-0.08, 0.08)
        noise_hum = random.uniform(-0.2, 0.2)
        noise_press = random.uniform(-0.04, 0.04)

        tilt_x = baseline["tilt_x_deg"] + noise_tilt
        tilt_y = baseline["tilt_y_deg"] + noise_tilt * 0.5
        disp = baseline["displacement_mm"] + noise_disp
        disp_rate = baseline["displacement_rate_mm_hr"]
        vib = baseline["vibration_rms_g"] + noise_vib
        temp = baseline["temperature_c"] + noise_temp
        hum = baseline["humidity_pct"] + noise_hum
        press = baseline["pressure_hpa"] + noise_press
        crack_w = baseline["crack_width_mm"]
        crack_flag = baseline["crack_detected"]

        # Accelerometer, Gyroscope & Magnetometer baseline noise
        ax = baseline["accel_x_g"] + noise_tilt * 0.1
        ay = baseline["accel_y_g"] + noise_tilt * 0.05
        az = baseline["accel_z_g"] + random.uniform(-0.002, 0.002)
        gx = baseline["gyro_x_dps"] + random.uniform(-0.005, 0.005)
        gy = baseline["gyro_y_dps"] + random.uniform(-0.005, 0.005)
        gz = baseline["gyro_z_dps"] + random.uniform(-0.002, 0.002)
        mx = baseline["mag_x_ut"] + random.uniform(-0.1, 0.1)
        my = baseline["mag_y_ut"] + random.uniform(-0.1, 0.1)
        mz = baseline["mag_z_ut"] + random.uniform(-0.1, 0.1)

        # Primary SIH Demonstration Scenario — NODE_03 Deformation
        if node_code == "NODE_03":
            if self.mode == "ANOMALY_NODE_03":
                severity_factor = 0.95
            elif self.mode == "NORMAL":
                severity_factor = 0.0
            else:
                # Continuous smooth cycle: 60-step cycle with progressive deformation
                cycle = (step % 90)
                if cycle > 25:
                    severity_factor = min(1.0, (cycle - 25) / 35.0)
                else:
                    severity_factor = 0.0

            if severity_factor > 0:
                # Progressive Inward Ground Movement & Accelerating Rate
                disp = baseline["displacement_mm"] + (severity_factor * 24.5)
                disp_rate = 0.3 + (severity_factor * 2.6)
                # MPU9250 Strata Tilt & Dynamic Vibration Spike
                tilt_x = baseline["tilt_x_deg"] + (severity_factor * 3.9)
                tilt_y = baseline["tilt_y_deg"] + (severity_factor * 1.8)
                vib = baseline["vibration_rms_g"] + (severity_factor * 0.46)
                ax = (severity_factor * 0.32)
                ay = (severity_factor * 0.16)
                gx = (severity_factor * 1.1)
                # Mechanical Crack Gauge Opening & Fissure Event
                crack_w = severity_factor * 3.6
                crack_flag = crack_w > 0.8
                # Atmospheric pressure drop
                press = baseline["pressure_hpa"] - (severity_factor * 7.5)

        elif node_code in self.watch_nodes:
            # Minor secondary deformation on adjacent neighbor node (NODE_04)
            cycle = (step % 90)
            if cycle > 35:
                severity_factor = min(0.4, (cycle - 35) / 50.0)
                disp = baseline["displacement_mm"] + (severity_factor * 6.0)
                disp_rate = 0.1 + (severity_factor * 0.5)
                tilt_x = baseline["tilt_x_deg"] + (severity_factor * 1.1)
                vib = baseline["vibration_rms_g"] + (severity_factor * 0.10)
                crack_w = severity_factor * 0.7
                crack_flag = crack_w > 0.5

        total_tilt = math.sqrt(tilt_x**2 + tilt_y**2)

        return {
            "is_online": True,
            # MPU9250 Motion
            "total_tilt_deg": round(total_tilt, 4),
            "tilt_x_deg": round(tilt_x, 4),
            "tilt_y_deg": round(tilt_y, 4),
            "vibration_rms_g": round(vib, 4),
            "accel_x_g": round(ax, 4),
            "accel_y_g": round(ay, 4),
            "accel_z_g": round(az, 4),
            "gyro_x_dps": round(gx, 4),
            "gyro_y_dps": round(gy, 4),
            "gyro_z_dps": round(gz, 4),
            "mag_x_ut": round(mx, 2),
            "mag_y_ut": round(my, 2),
            "mag_z_ut": round(mz, 2),
            # BME280 Environment
            "temperature_c": round(temp, 2),
            "humidity_pct": round(hum, 2),
            "pressure_hpa": round(press, 2),
            # Displacement & Crack
            "displacement_mm": round(disp, 3),
            "displacement_rate_mm_hr": round(disp_rate, 3),
            "displacement_baseline_mm": baseline.get("displacement_baseline_mm", 1.0),
            "crack_width_mm": round(crack_w, 3),
            "crack_status": crack_flag,
            "crack_detected": crack_flag,
            # Power
            "battery_voltage_v": round(baseline["battery_voltage_v"] - (step * 0.00001), 3),
            "battery_pct": baseline["battery_pct"]
        }

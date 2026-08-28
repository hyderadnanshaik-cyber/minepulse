"""
=============================================================================
RED HACK Mine Subsidence Monitoring System (SIH26025)
Feature Engineering Pipeline
-----------------------------------------------------------------------------
Computes dynamic physical rates, sliding-window statistics, spatial correlation
indicators, and baseline deviations for ML anomaly detection.
=============================================================================
"""

import math
import numpy as np
import pandas as pd
from typing import Dict, Any, List, Union

FEATURE_COLUMNS = [
    "total_tilt_deg",
    "tilt_rate_deg_per_hr",
    "displacement_mm",
    "displacement_rate_mm_per_hr",
    "vibration_rms_g",
    "vibration_rolling_mean_3",
    "displacement_delta_baseline",
    "tilt_delta_baseline",
    "crack_status",
    "neighbor_anomaly_count",
    "subsidence_velocity_index"
]

class FeatureEngineer:
    """
    Stateful and stateless feature engineering engine for mine subsidence telemetry.
    Supports single-sample real-time streaming inference and batch historical training data.
    """
    def __init__(self):
        # In-memory historical buffers per node for real-time edge streaming
        # format: {node_id: {"history": deque(maxlen=10), "baseline": dict}}
        self.node_buffers: Dict[str, Dict[str, Any]] = {}
        
    def init_node_baseline(self, node_id: str, baseline_tilt: float, baseline_disp: float):
        """Initializes calibrated baseline values for a specific sensor node."""
        if node_id not in self.node_buffers:
            self.node_buffers[node_id] = {"history": [], "baseline": {}}
        self.node_buffers[node_id]["baseline"] = {
            "tilt": baseline_tilt,
            "displacement": baseline_disp
        }

    def transform_dataframe(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Batch feature transformation on historical / training DataFrame.
        Groups by node_id and calculates time-series derivatives.
        """
        data = df.copy()
        
        # Ensure timestamp is datetime
        if not pd.api.types.is_datetime64_any_dtype(data["timestamp"]):
            data["timestamp"] = pd.to_datetime(data["timestamp"])
            
        data = data.sort_values(by=["node_id", "timestamp"]).reset_index(drop=True)
        
        # Calculate total tilt if missing
        if "total_tilt_deg" not in data.columns and "tilt_x_deg" in data.columns and "tilt_y_deg" in data.columns:
            data["total_tilt_deg"] = np.sqrt(data["tilt_x_deg"]**2 + data["tilt_y_deg"]**2)
            
        # Grouped time delta (in hours)
        data["time_diff_sec"] = data.groupby("node_id")["timestamp"].diff().dt.total_seconds().fillna(30.0)
        data["time_diff_hr"] = data["time_diff_sec"] / 3600.0
        data["time_diff_hr"] = data["time_diff_hr"].replace(0, 30.0 / 3600.0)
        
        # Tilt Rate (deg / hr)
        data["tilt_diff"] = data.groupby("node_id")["total_tilt_deg"].diff().fillna(0.0)
        data["tilt_rate_deg_per_hr"] = (data["tilt_diff"] / data["time_diff_hr"]).clip(-50.0, 50.0)
        
        # Displacement Rate (mm / hr)
        data["disp_diff"] = data.groupby("node_id")["displacement_mm"].diff().fillna(0.0)
        data["displacement_rate_mm_per_hr"] = (data["disp_diff"] / data["time_diff_hr"]).clip(-200.0, 200.0)
        
        # Rolling Vibration Average (Window size 3)
        data["vibration_rolling_mean_3"] = data.groupby("node_id")["vibration_rms_g"].transform(
            lambda s: s.rolling(3, min_periods=1).mean()
        )
        
        # Baselines per node (first 10 samples average as calibrated baseline)
        baselines = data.groupby("node_id").head(10).groupby("node_id").agg({
            "total_tilt_deg": "mean",
            "displacement_mm": "mean"
        }).reset_index().rename(columns={
            "total_tilt_deg": "baseline_tilt",
            "displacement_mm": "baseline_disp"
        })
        
        data = pd.merge(data, baselines, on="node_id", how="left")
        data["displacement_delta_baseline"] = data["displacement_mm"] - data["baseline_disp"]
        data["tilt_delta_baseline"] = data["total_tilt_deg"] - data["baseline_tilt"]
        
        # Subsidence Velocity Index (composite dynamic metric)
        # SVI = |tilt_rate| * 2.0 + |displacement_rate| * 1.5 + (vibration_rms * 10) + (crack_status * 20)
        data["subsidence_velocity_index"] = (
            np.abs(data["tilt_rate_deg_per_hr"]) * 2.0 +
            np.abs(data["displacement_rate_mm_per_hr"]) * 1.5 +
            (data["vibration_rms_g"] * 10.0) +
            (data["crack_status"] * 25.0)
        )
        
        # Neighbor anomaly count default if missing
        if "neighbor_anomaly_count" not in data.columns:
            data["neighbor_anomaly_count"] = 0
            
        return data

    def extract_streaming_features(self, sample: Dict[str, Any]) -> Dict[str, float]:
        """
        Transforms a single live telemetry reading dictionary into ML-ready feature vector.
        """
        node_id = sample.get("node_id", "UNKNOWN")
        tilt_x = float(sample.get("tilt_x_deg", sample.get("tilt_x", 0.0)))
        tilt_y = float(sample.get("tilt_y_deg", sample.get("tilt_y", 0.0)))
        total_tilt = sample.get("total_tilt_deg", math.sqrt(tilt_x**2 + tilt_y**2))
        disp = float(sample.get("displacement_mm", sample.get("displacement", 0.0)))
        vib = float(sample.get("vibration_rms_g", sample.get("vibration_rms", sample.get("vibration", 0.02))))
        crack = int(sample.get("crack_status", 0))
        neighbor_anomalies = int(sample.get("neighbor_anomaly_count", 0))
        
        if node_id not in self.node_buffers:
            self.node_buffers[node_id] = {
                "history": [],
                "baseline": {"tilt": total_tilt, "displacement": disp}
            }
            
        history = self.node_buffers[node_id]["history"]
        baseline = self.node_buffers[node_id]["baseline"]
        
        # Time delta estimation
        dt_hr = (30.0 / 3600.0) # Default 30s period
        if len(history) > 0:
            last_sample = history[-1]
            tilt_rate = (total_tilt - last_sample["total_tilt_deg"]) / dt_hr
            disp_rate = (disp - last_sample["displacement_mm"]) / dt_hr
            vib_window = [h["vibration_rms_g"] for h in history[-2:]] + [vib]
            vib_rolling = sum(vib_window) / len(vib_window)
        else:
            tilt_rate = 0.0
            disp_rate = 0.0
            vib_rolling = vib
            
        # Update buffer
        history.append({
            "total_tilt_deg": total_tilt,
            "displacement_mm": disp,
            "vibration_rms_g": vib
        })
        if len(history) > 10:
            history.pop(0)
            
        disp_delta_base = disp - baseline.get("displacement", disp)
        tilt_delta_base = total_tilt - baseline.get("tilt", total_tilt)
        
        svi = (
            abs(tilt_rate) * 2.0 +
            abs(disp_rate) * 1.5 +
            (vib * 10.0) +
            (crack * 25.0)
        )
        
        return {
            "total_tilt_deg": round(float(total_tilt), 4),
            "tilt_rate_deg_per_hr": round(float(np.clip(tilt_rate, -50.0, 50.0)), 4),
            "displacement_mm": round(float(disp), 4),
            "displacement_rate_mm_per_hr": round(float(np.clip(disp_rate, -200.0, 200.0)), 4),
            "vibration_rms_g": round(float(vib), 4),
            "vibration_rolling_mean_3": round(float(vib_rolling), 4),
            "displacement_delta_baseline": round(float(disp_delta_base), 4),
            "tilt_delta_baseline": round(float(tilt_delta_base), 4),
            "crack_status": crack,
            "neighbor_anomaly_count": neighbor_anomalies,
            "subsidence_velocity_index": round(float(svi), 4)
        }

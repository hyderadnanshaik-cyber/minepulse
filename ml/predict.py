"""
=============================================================================
RED HACK Mine Subsidence Monitoring System (SIH26025)
Real-Time Inference & Risk Assessment Service
-----------------------------------------------------------------------------
Loads trained IsolationForest and Scaler models to deliver low-latency
anomaly inference and multi-factor risk assessment on live sensor telemetry.
=============================================================================
"""

import os
import sys
import json
import argparse
import joblib
import numpy as np
import pandas as pd
from typing import Dict, Any, List, Union

from feature_engineering import FeatureEngineer, FEATURE_COLUMNS
from risk_engine import RiskEngine

class MineSubsidencePredictor:
    """
    Production-ready inference wrapper for real-time edge or server deployment.
    """
    def __init__(self, model_dir: str = "ml/model"):
        self.model_dir = model_dir
        self.model_path = os.path.join(model_dir, "isolation_forest.joblib")
        self.scaler_path = os.path.join(model_dir, "feature_scaler.joblib")
        self.meta_path = os.path.join(model_dir, "model_metadata.json")
        
        self.model = None
        self.scaler = None
        self.metadata = {}
        self.min_dec = -0.3
        self.max_dec = 0.3
        
        self.feature_engineer = FeatureEngineer()
        self.risk_engine = RiskEngine()
        
        self._load_artifacts()

    def _load_artifacts(self):
        if os.path.exists(self.model_path) and os.path.exists(self.scaler_path):
            self.model = joblib.load(self.model_path)
            self.scaler = joblib.load(self.scaler_path)
            
            if os.path.exists(self.meta_path):
                with open(self.meta_path, "r") as f:
                    self.metadata = json.load(f)
                    norm = self.metadata.get("score_normalization", {})
                    self.min_dec = norm.get("min_decision_value", -0.3)
                    self.max_dec = norm.get("max_decision_value", 0.3)
            print(f"[PREDICTOR] Loaded IsolationForest model & scaler from {self.model_dir}")
        else:
            print(f"[PREDICTOR WARNING] Model artifacts not found in {self.model_dir}. Operating in Rule-Based fallback mode.")

    def predict_single(self, telemetry: Dict[str, Any]) -> Dict[str, Any]:
        """
        Executes end-to-end inference on a single incoming telemetry dictionary.
        
        Args:
            telemetry: Raw packet e.g. {
                "node_id": "NODE_008",
                "tilt_x_deg": 3.4,
                "tilt_y_deg": 1.2,
                "displacement_mm": 14.5,
                "vibration_rms_g": 0.35,
                "crack_status": 0,
                "battery_voltage_v": 3.95,
                "temperature_c": 31.0
            }
        """
        node_id = telemetry.get("node_id", "UNKNOWN_NODE")
        
        # 1. Feature Engineering
        feats = self.feature_engineer.extract_streaming_features(telemetry)
        
        # 2. ML Inference (if model loaded)
        ml_anomaly_score = 0.0
        ml_is_anomaly = False
        
        if self.model is not None and self.scaler is not None:
            # Build feature array in strict column order
            feat_vector = np.array([[feats.get(col, 0.0) for col in FEATURE_COLUMNS]])
            scaled_vector = self.scaler.transform(feat_vector)
            
            # Predict
            pred_class = self.model.predict(scaled_vector)[0] # -1 anomaly, 1 normal
            ml_is_anomaly = (pred_class == -1)
            
            raw_dec = self.model.decision_function(scaled_vector)[0]
            # Normalize to [0.0, 1.0] (higher = more anomalous)
            norm_score = 1.0 - ((raw_dec - self.min_dec) / (self.max_dec - self.min_dec + 1e-9))
            ml_anomaly_score = float(np.clip(norm_score, 0.0, 1.0))
        else:
            # Fallback heuristic score
            ml_anomaly_score = min(1.0, feats.get("subsidence_velocity_index", 0.0) / 50.0)
            ml_is_anomaly = ml_anomaly_score > 0.5
            
        # 3. Risk Engine Calculation
        risk_result = self.risk_engine.evaluate_node_risk(
            node_id=node_id,
            features=feats,
            ml_anomaly_score=ml_anomaly_score,
            ml_is_anomaly=ml_is_anomaly
        )
        
        return {
            "node_id": node_id,
            "timestamp": telemetry.get("timestamp", pd.Timestamp.now().isoformat()),
            "risk_score": risk_result["risk_score"],
            "risk_level": risk_result["risk_level"],
            "color_code": risk_result["color_code"],
            "ml_anomaly_score": risk_result["ml_anomaly_score"],
            "ml_is_anomaly": risk_result["ml_is_anomaly"],
            "engineered_features": feats,
            "triggered_rules": risk_result["triggered_rules"],
            "recommended_action": risk_result["recommended_action"]
        }

    def predict_batch(self, telemetry_list: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Processes a list of telemetry events."""
        return [self.predict_single(item) for item in telemetry_list]

def run_cli():
    parser = argparse.ArgumentParser(description="RED HACK Mine Subsidence Predictor CLI")
    parser.add_argument("--eval-sample", action="store_true", help="Run inference on test samples across all risk tiers")
    parser.add_argument("--file", type=str, help="Path to CSV or JSON file to score")
    parser.add_argument("--model-dir", type=str, default="ml/model", help="Path to model directory")
    args = parser.parse_args()

    predictor = MineSubsidencePredictor(model_dir=args.model_dir)

    if args.eval_sample:
        test_cases = [
            {
                "name": "Case 1: Nominal Baseline",
                "telemetry": {"node_id": "NODE_001", "tilt_x_deg": 0.05, "tilt_y_deg": -0.02, "displacement_mm": 3.1, "vibration_rms_g": 0.02, "crack_status": 0}
            },
            {
                "name": "Case 2: Early Warning Tilt Shift",
                "telemetry": {"node_id": "NODE_002", "tilt_x_deg": 2.5, "tilt_y_deg": 1.1, "displacement_mm": 9.2, "vibration_rms_g": 0.12, "crack_status": 0}
            },
            {
                "name": "Case 3: High Risk Dynamic Subsidence",
                "telemetry": {"node_id": "NODE_008", "tilt_x_deg": 5.2, "tilt_y_deg": 3.8, "displacement_mm": 22.0, "vibration_rms_g": 0.65, "crack_status": 0}
            },
            {
                "name": "Case 4: Critical Break-Wire Severed & Roof Failure",
                "telemetry": {"node_id": "NODE_013", "tilt_x_deg": 9.1, "tilt_y_deg": 6.4, "displacement_mm": 34.8, "vibration_rms_g": 1.45, "crack_status": 1}
            }
        ]
        
        print("\n================== DEMO PREDICTION EVALUATION ==================")
        for case in test_cases:
            print(f"\n--- {case['name']} ---")
            res = predictor.predict_single(case["telemetry"])
            print(json.dumps(res, indent=2))
        print("================================================================\n")

if __name__ == "__main__":
    run_cli()

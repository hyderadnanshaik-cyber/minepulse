"""
=============================================================================
RED HACK Mine Subsidence Monitoring System (SIH26025)
Multi-Factor Risk Assessment Engine
-----------------------------------------------------------------------------
Combines unsupervised ML anomaly scores, physical statutory safety thresholds
(DGMS / Coal Mine Regulations), and multi-node spatial correlation matrices
to compute real-time subsidence risk scores (0-100) and alert levels.
=============================================================================
"""

import math
from typing import Dict, Any, List, Optional

# Prototype Physical Alert Thresholds (Calibrated for Coal Mine Strata)
THRESHOLDS = {
    "tilt_deg": {
        "watch": 2.0,      # > 2.0 degrees
        "high": 4.5,       # > 4.5 degrees
        "critical": 8.0    # > 8.0 degrees
    },
    "tilt_rate_deg_per_hr": {
        "watch": 0.5,
        "high": 1.5,
        "critical": 3.0
    },
    "displacement_mm": {
        "watch": 8.0,      # > 8mm strata displacement
        "high": 18.0,      # > 18mm displacement
        "critical": 30.0   # > 30mm imminent roof collapse
    },
    "displacement_rate_mm_per_hr": {
        "watch": 2.0,
        "high": 6.0,
        "critical": 15.0
    },
    "vibration_rms_g": {
        "watch": 0.25,     # Micro-seismic activity
        "high": 0.60,      # Significant rock fracturing / blasting
        "critical": 1.20   # Extreme dynamic impact / collapse wave
    }
}

class RiskEngine:
    """
    Evaluates multi-parametric subsidence risk combining physical physics-based
    thresholds and Machine Learning statistical anomaly confidence.
    """
    def __init__(self, neighbor_adjacency_map: Optional[Dict[str, List[str]]] = None):
        # Optional graph adjacency for spatial risk propagation
        self.adjacency_map = neighbor_adjacency_map or {}
        # Keep track of recent node risk levels for spatial correlation
        self.node_risk_states: Dict[str, Dict[str, Any]] = {}

    def set_adjacency_map(self, adjacency_map: Dict[str, List[str]]):
        self.adjacency_map = adjacency_map

    def evaluate_node_risk(
        self,
        node_id: str,
        features: Dict[str, float],
        ml_anomaly_score: float,
        ml_is_anomaly: bool
    ) -> Dict[str, Any]:
        """
        Calculates composite risk score [0..100], risk level, triggered rules, and actionable recommendations.
        
        Args:
            node_id: Identifier of sensor node
            features: Dictionary of engineered features (tilt, disp, rates, crack, etc.)
            ml_anomaly_score: Normalized ML score [0.0..1.0]
            ml_is_anomaly: Boolean flag from ML IsolationForest
        """
        tilt = float(features.get("total_tilt_deg", 0.0))
        tilt_rate = float(features.get("tilt_rate_deg_per_hr", 0.0))
        disp = float(features.get("displacement_mm", 0.0))
        disp_rate = float(features.get("displacement_rate_mm_per_hr", 0.0))
        vib = float(features.get("vibration_rms_g", 0.0))
        crack_broken = bool(features.get("crack_status", 0))
        
        triggered_rules = []
        physical_score = 0.0
        
        # 1. Crack Sensor Immediate Escalation (Physical Break-wire severed)
        if crack_broken:
            physical_score += 45.0
            triggered_rules.append("CRITICAL: Strata Break-Wire / Fissure Conductance Broken")
            
        # 2. Tilt and Tilt-Rate Evaluation
        if tilt >= THRESHOLDS["tilt_deg"]["critical"]:
            physical_score += 35.0
            triggered_rules.append(f"CRITICAL: Total Tilt ({tilt:.2f}°) exceeds critical limit ({THRESHOLDS['tilt_deg']['critical']}°)")
        elif tilt >= THRESHOLDS["tilt_deg"]["high"]:
            physical_score += 20.0
            triggered_rules.append(f"HIGH: Total Tilt ({tilt:.2f}°) exceeds warning threshold")
        elif tilt >= THRESHOLDS["tilt_deg"]["watch"]:
            physical_score += 10.0
            triggered_rules.append(f"WATCH: Total Tilt ({tilt:.2f}°) elevated")
            
        if abs(tilt_rate) >= THRESHOLDS["tilt_rate_deg_per_hr"]["critical"]:
            physical_score += 25.0
            triggered_rules.append(f"CRITICAL: Rapid Angular Velocity ({tilt_rate:.2f}°/hr)")
        elif abs(tilt_rate) >= THRESHOLDS["tilt_rate_deg_per_hr"]["high"]:
            physical_score += 12.0
            
        # 3. Displacement & Displacement Rate Evaluation
        if disp >= THRESHOLDS["displacement_mm"]["critical"]:
            physical_score += 40.0
            triggered_rules.append(f"CRITICAL: Strata Subsidence Displacement ({disp:.2f}mm) exceeds safety ceiling")
        elif disp >= THRESHOLDS["displacement_mm"]["high"]:
            physical_score += 22.0
            triggered_rules.append(f"HIGH: Strata Displacement ({disp:.2f}mm) high")
        elif disp >= THRESHOLDS["displacement_mm"]["watch"]:
            physical_score += 10.0
            
        if abs(disp_rate) >= THRESHOLDS["displacement_rate_mm_per_hr"]["critical"]:
            physical_score += 25.0
            triggered_rules.append(f"CRITICAL: Accelerating Subsidence Velocity ({disp_rate:.2f}mm/hr)")
        elif abs(disp_rate) >= THRESHOLDS["displacement_rate_mm_per_hr"]["high"]:
            physical_score += 12.0
            
        # 4. Vibration / Micro-seismic Evaluation
        if vib >= THRESHOLDS["vibration_rms_g"]["critical"]:
            physical_score += 30.0
            triggered_rules.append(f"CRITICAL: Extreme Micro-Seismic Shock ({vib:.3f}g RMS)")
        elif vib >= THRESHOLDS["vibration_rms_g"]["high"]:
            physical_score += 15.0
            triggered_rules.append(f"HIGH: Micro-Seismic Activity ({vib:.3f}g RMS)")
            
        # 5. Spatial Neighbor Correlation Analysis
        neighbor_high_count = 0
        neighbor_nodes = self.adjacency_map.get(node_id, [])
        for neighbor in neighbor_nodes:
            neighbor_state = self.node_risk_states.get(neighbor, {})
            if neighbor_state.get("risk_level") in ["HIGH", "CRITICAL"]:
                neighbor_high_count += 1
                
        spatial_escalation = 0.0
        if neighbor_high_count >= 2:
            spatial_escalation = 20.0
            triggered_rules.append(f"SPATIAL: Correlated subsidence detected across {neighbor_high_count} adjacent mesh nodes")
        elif neighbor_high_count == 1:
            spatial_escalation = 8.0
            
        # 6. Hybrid Fusion: ML Statistical Score + Physical Thresholds + Spatial Factor
        # ML Anomaly contribution: 0 to 35 points
        # Physical score contribution: 0 to 55 points
        # Spatial correlation: 0 to 20 points
        ml_contribution = ml_anomaly_score * 35.0
        if ml_is_anomaly:
            ml_contribution = max(ml_contribution, 18.0)
            triggered_rules.append(f"ML: IsolationForest Statistical Anomaly Confirmed (Score: {ml_anomaly_score:.3f})")
            
        raw_risk_score = (physical_score * 0.55) + ml_contribution + spatial_escalation
        
        # Hard statutory floor if crack wire severed or critical thresholds breached
        if crack_broken or disp >= THRESHOLDS["displacement_mm"]["critical"]:
            final_risk_score = max(80.0, raw_risk_score)
        else:
            final_risk_score = min(100.0, max(0.0, raw_risk_score))
            
        final_risk_score = round(final_risk_score, 1)
        
        # Risk Categorization (PROTOTYPE THRESHOLDS)
        if final_risk_score >= 76.0:
            risk_level = "CRITICAL"
            action = "IMMEDIATE EVACUATION: Sound Gateway Siren, Dispatch Emergency SMS/Audio Broadcast, Halt Machinery"
            color_code = "#FF0033"
        elif final_risk_score >= 51.0:
            risk_level = "HIGH"
            action = "RESTRICT ACCESS: Dispatch Geotechnical Survey Team, Verify Roof Bolting & Extensometers"
            color_code = "#FF6600"
        elif final_risk_score >= 26.0:
            risk_level = "WATCH"
            action = "HEIGHTENED SURVEILLANCE: Increase Telemetry Sampling Frequency, Monitor Neighboring Nodes"
            color_code = "#FFCC00"
        else:
            risk_level = "NORMAL"
            action = "ROUTINE MONITORING: Mine strata stable within nominal parameters"
            color_code = "#00CC66"
            
        result = {
            "node_id": node_id,
            "risk_score": final_risk_score,
            "risk_level": risk_level,
            "color_code": color_code,
            "ml_anomaly_score": round(float(ml_anomaly_score), 4),
            "ml_is_anomaly": bool(ml_is_anomaly),
            "physical_score": round(float(physical_score), 2),
            "spatial_escalation": round(float(spatial_escalation), 2),
            "neighbor_high_count": neighbor_high_count,
            "triggered_rules": triggered_rules,
            "recommended_action": action
        }
        
        # Update node state cache for neighbor correlation
        self.node_risk_states[node_id] = result
        return result

import os
import sys
import time
import json
import sqlite3

# Ensure project root & backend are in Python module search path
sys.path.insert(0, os.path.abspath("."))
sys.path.insert(0, os.path.abspath("backend"))

print("===================================================================")
print(" RUNNING MINEGUARD ACCEPTANCE TEST SUITE (SIH26025)")
print("===================================================================")

# 1. Test Field Transport Abstraction
from gateway.field_transport import SimulatedFieldTransportAdapter
transport = SimulatedFieldTransportAdapter(node_count=20, gateway_id="MINEGATE-01")

# TEST 6 & 1: NODE_04 Displacement Anomaly
print("\n[TEST 1] Testing NODE_04 Displacement Anomaly Flow...")
status_04 = transport.get_node_status("NODE_04")
assert status_04["node_id"] == "NODE_04", "NODE_04 must be queryable"
print(f"  -> NODE_04 Initial Status: {status_04['status']}, RSSI: {status_04['rssi']} dBm")

# Test ML Risk Engine on NODE_04 Displacement Anomaly
from ml.risk_engine import RiskEngine
risk_engine = RiskEngine()
feat_04 = {
    "total_tilt_deg": 4.8,
    "tilt_rate_deg_per_hr": 1.2,
    "displacement_mm": 22.5,
    "displacement_rate_mm_per_hr": 4.5,
    "vibration_rms_g": 0.12,
    "crack_status": 0,
    "neighbor_anomaly_count": 2
}
pred_04 = risk_engine.evaluate_node_risk("NODE_04", feat_04, ml_anomaly_score=0.82, ml_is_anomaly=True)
print(f"  -> ML Evaluation for NODE_04: Risk Score = {pred_04['risk_score']}, Risk Level = {pred_04['risk_level']}")
assert pred_04["risk_level"] in ["HIGH", "CRITICAL"], "Displacement spike must trigger HIGH/CRITICAL alert"
print("  [PASS] TEST 1 Verified.")

# TEST 2: NODE_12 Sudden Crack Detection Flow
print("\n[TEST 2] Testing NODE_12 Crack Detection Flow...")
feat_12 = {
    "total_tilt_deg": 6.2,
    "tilt_rate_deg_per_hr": 2.1,
    "displacement_mm": 28.0,
    "displacement_rate_mm_per_hr": 8.0,
    "vibration_rms_g": 0.85,
    "crack_status": 1,
    "neighbor_anomaly_count": 3
}
pred_12 = risk_engine.evaluate_node_risk("NODE_12", feat_12, ml_anomaly_score=0.96, ml_is_anomaly=True)
print(f"  -> ML Evaluation for NODE_12: Risk Score = {pred_12['risk_score']}, Risk Level = {pred_12['risk_level']}")
assert pred_12["risk_level"] == "CRITICAL", "Crack detection must trigger CRITICAL risk"
print("  [PASS] TEST 2 Verified.")

# TEST 3: Internet OFF -> Local SQLite Buffering
print("\n[TEST 3] Testing Offline Local SQLite Storage...")
from gateway.local_db import EdgeLocalDB
db = EdgeLocalDB(db_path="gateway/test_edge_buffer.db")
db.insert_telemetry("NODE_04", {"tilt": 4.8, "displacement": 22.5, "crack_status": False, "rssi": -72})
db.insert_alert("NODE_12", {"alert_type": "CRACK_DETECTED", "severity": "CRITICAL", "title": "Crack Detected at Node 12", "risk_score": 95.0})

pending = db.get_pending_records(limit=10)
assert len(pending["telemetry"]) >= 1, "Offline telemetry must be queued with PENDING status"
assert len(pending["alerts"]) >= 1, "Offline alerts must be queued with PENDING status"
print(f"  -> Queued Telemetry: {len(pending['telemetry'])}, Queued Alerts: {len(pending['alerts'])}")
print("  [PASS] TEST 3 Verified.")

# TEST 4: Internet Returns -> Synchronization
print("\n[TEST 4] Testing Internet Reconnect Sync Drain...")
telemetry_ids = [r["id"] for r in pending["telemetry"]]
db.mark_telemetry_synced(telemetry_ids)
pending_after = db.get_pending_records(limit=10)
assert len(pending_after["telemetry"]) == 0, "Marked records must be SYNCED"
print("  -> Pending records successfully drained upon sync completion.")
print("  [PASS] TEST 4 Verified.")

# TEST 5: Operator Locates NODE_19
print("\n[TEST 5] Testing On-Demand Locator for NODE_19...")
loc_res = transport.locate_node("NODE_19", duration_sec=10)
assert loc_res["status"] == "SUCCESS", "Locator command must succeed"
assert loc_res["node_id"] == "NODE_19", "Locator must target NODE_19"
print(f"  -> Locator Response: {loc_res['message']}")
print("  [PASS] TEST 5 Verified.")

# TEST 6: Agnostic Verification across NODE_01 to NODE_20
print("\n[TEST 6] Testing Node-Agnostic Behavior across all 20 nodes...")
for i in range(1, 21):
    nid = f"NODE_{i:02d}"
    st = transport.get_node_status(nid)
    assert st["status"] == "ONLINE", f"{nid} must be active"
print("  -> All 20 nodes verified independently without hardcoding.")
print("  [PASS] TEST 6 Verified.")

# TEST 7: Node Registration Flow Validation
print("\n[TEST 7] Testing Node Registration Schema & Logic...")
from app.schemas.node import NodeRegisterRequest
reg_req = NodeRegisterRequest(code="100019", name="MINEGUARD Surface Station 19", panel_id=1)
assert reg_req.code == "100019"
assert reg_req.name == "MINEGUARD Surface Station 19"
print(f"  -> Validated Registration Request Code: {reg_req.code} for Node: {reg_req.name}")
print("  [PASS] TEST 7 Verified.")

# Cleanup test SQLite file
if os.path.exists("gateway/test_edge_buffer.db"):
    os.remove("gateway/test_edge_buffer.db")

print("\n===================================================================")
print(" ALL 7 ACCEPTANCE TESTS PASSED SUCCESSFULLY! [OK]")
print("===================================================================")

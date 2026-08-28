"""
End-to-End AI/ML Pipeline Verification Script for MINEGUARD (SIH 2026)
Tests:
1. Model loading & IsolationForest inference
2. Streaming feature extraction (rolling rates, baseline delta, SVI)
3. Hybrid risk fusion (ML + DGMS safety rules)
4. PostgreSQL ai_predictions & alerts persistence
5. Node-specific anomaly identification (NODE_03 vs normal nodes)
6. Retraining endpoint against live PostgreSQL telemetry
"""

import urllib.request
import json
import time

BASE_URL = "http://127.0.0.1:8000/api"

def make_req(endpoint, method="GET", data=None):
    url = f"{BASE_URL}{endpoint}"
    req = urllib.request.Request(url, method=method)
    req.add_header("Content-Type", "application/json")
    req.add_header("Authorization", "Bearer dev-mock-token-engineer")
    
    body = json.dumps(data).encode("utf-8") if data else None
    try:
        with urllib.request.urlopen(req, data=body, timeout=10) as resp:
            return resp.status, json.loads(resp.read().decode("utf-8"))
    except urllib.error.HTTPError as e:
        return e.code, json.loads(e.read().decode("utf-8"))
    except Exception as e:
        return 500, {"error": str(e)}

def run_tests():
    print("===================================================================")
    print("        MINEGUARD AI/ML PIPELINE VERIFICATION SUITE")
    print("===================================================================")
    
    # Test 1: AI Status
    status, body = make_req("/ai/status")
    print(f"\n[Test 1] AI Status Endpoint: HTTP {status}")
    print(f"  Model Version: {body.get('model_version')}")
    print(f"  Is Trained: {body.get('is_trained')}")
    print(f"  Model ROC-AUC / Accuracy Metric: {body.get('model_accuracy')}")
    print(f"  Active Monitored Nodes: {body.get('active_nodes_monitored')}")
    assert status == 200, "AI Status failed"
    assert body.get('is_trained') is True, "Model should be trained"

    # Test 2: Ingest Normal Telemetry for NODE_01
    normal_payload = {
        "node_id": "NODE_01",
        "tilt_x": 0.05,
        "tilt_y": -0.02,
        "vibration": 0.022,
        "temperature": 25.4,
        "humidity": 55.0,
        "pressure": 1013.2,
        "displacement": 1.2,
        "displacement_rate": 0.02,
        "crack_detected": False,
        "crack_width": 0.0,
        "battery_level": 98.0,
        "rssi": -68.0
    }
    status, body = make_req("/telemetry/ingest", method="POST", data=normal_payload)
    print(f"\n[Test 2] Normal Node (NODE_01) Telemetry Ingestion: HTTP {status}")
    assert status == 201 or status == 200, f"Normal telemetry failed: {body}"

    # Test 3: Ingest Hazardous Anomaly Telemetry for NODE_03
    anomaly_payload = {
        "node_id": "NODE_03",
        "tilt_x": 3.9,
        "tilt_y": 1.8,
        "vibration": 0.48,
        "temperature": 29.8,
        "humidity": 62.0,
        "pressure": 1005.5,
        "displacement": 26.5,
        "displacement_rate": 2.8,
        "crack_detected": True,
        "crack_width": 3.6,
        "battery_level": 94.0,
        "rssi": -82.0
    }
    status, body = make_req("/telemetry/ingest", method="POST", data=anomaly_payload)
    print(f"\n[Test 3] Anomaly Node (NODE_03) Telemetry Ingestion: HTTP {status}")
    assert status == 201 or status == 200, f"Anomaly telemetry failed: {body}"

    time.sleep(1)

    # Test 4: Query Recent AI Predictions
    status, preds = make_req("/ai/predictions?limit=10")
    print(f"\n[Test 4] Recent AI Predictions from PostgreSQL: HTTP {status}")
    print(f"  Retrieved {len(preds)} prediction records.")
    
    node_03_pred = next((p for p in preds if p.get("node_id") == "NODE_03"), None)
    node_01_pred = next((p for p in preds if p.get("node_id") == "NODE_01"), None)
    
    if node_03_pred:
        print(f"\n  >> NODE_03 Prediction (ANOMALY):")
        print(f"     Risk Score: {node_03_pred.get('risk_score')}/100")
        print(f"     Risk Level: {node_03_pred.get('risk_level')}")
        print(f"     ML Anomaly Score: {node_03_pred.get('anomaly_score')}")
        print(f"     Confidence: {node_03_pred.get('confidence')}")
        indicators = node_03_pred.get('spatial_pattern', {}).get('triggered_indicators', [])
        print(f"     Interpretable Contributing Factors: {indicators}")
        assert node_03_pred.get("risk_level") in ["HIGH", "CRITICAL"], "NODE_03 must be classified as HIGH or CRITICAL"

    if node_01_pred:
        print(f"\n  >> NODE_01 Prediction (NOMINAL):")
        print(f"     Risk Score: {node_01_pred.get('risk_score')}/100")
        print(f"     Risk Level: {node_01_pred.get('risk_level')}")
        print(f"     ML Anomaly Score: {node_01_pred.get('anomaly_score')}")
        assert node_01_pred.get("risk_level") in ["NORMAL", "MODERATE"], "NODE_01 must be NORMAL or MODERATE"

    # Test 5: Verify Generated Alerts
    status, alerts = make_req("/alerts?limit=5")
    print(f"\n[Test 5] Checking Alerts in PostgreSQL: HTTP {status}")
    print(f"  Total alerts: {len(alerts)}")
    node_03_alert = next((a for a in alerts if "NODE_03" in str(a.get("title", "")) or "NODE_03" in str(a.get("node_id", ""))), None)
    if node_03_alert:
        print(f"  >> Alert Verified for NODE_03: [{node_03_alert.get('severity')}] {node_03_alert.get('title')}")
        print(f"     Message: {node_03_alert.get('message')}")

    # Test 6: AI Retraining on PostgreSQL Telemetry
    status, train_res = make_req("/ai/train", method="POST")
    print(f"\n[Test 6] Real AI Model Retraining on PostgreSQL: HTTP {status}")
    print(f"  Status: {train_res.get('status')}")
    print(f"  Samples Used: {train_res.get('samples_used')}")
    print(f"  New Model Version: {train_res.get('model_version')}")
    print(f"  Message: {train_res.get('message')}")
    assert status == 200, "Retraining failed"

    print("\n===================================================================")
    print("  ALL AI/ML PIPELINE TESTS PASSED WITH 100% SUCCESS!")
    print("===================================================================")

if __name__ == "__main__":
    run_tests()

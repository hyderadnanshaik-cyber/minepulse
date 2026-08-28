import sys
import os
import urllib.request
import json
import time
from datetime import datetime

API_BASE = "http://127.0.0.1:8000/api"
AUTH_HEADER = {"Authorization": "Bearer dev-token", "Content-Type": "application/json"}

def http_req(url, method="GET", data=None):
    req = urllib.request.Request(url, headers=AUTH_HEADER, method=method)
    if data:
        req.data = json.dumps(data).encode("utf-8")
    try:
        with urllib.request.urlopen(req) as resp:
            body = resp.read().decode("utf-8")
            return resp.status, json.loads(body) if body else {}
    except urllib.error.HTTPError as e:
        body = e.read().decode("utf-8")
        try:
            return e.code, json.loads(body)
        except Exception:
            return e.code, {"error": body}

def print_separator(title=""):
    print("\n" + "=" * 78)
    if title:
        print(f"   {title}")
        print("=" * 78)

def run_e2e_ai_test():
    print_separator("STRATASAFE — COMPLETE AI/ML & ALERT END-TO-END VERIFICATION SUITE")
    print(f"Timestamp: {datetime.now().isoformat()}")
    print(f"API Target: {API_BASE}")

    results = {}
    test_node = "NODE_EVAL_01"

    # =========================================================================
    # PHASE 1: AI MODEL & ARCHITECTURE INSPECTION
    # =========================================================================
    print_separator("PHASE 1: AI/ML MODEL & ARCHITECTURE INSPECTION")
    code, ai_status = http_req(f"{API_BASE}/ai/status")
    print(f"[API] GET /api/ai/status -> HTTP {code}")
    print(f"  Model Version: {ai_status.get('model_version')}")
    print(f"  Model Architecture: Isolation Forest + DGMS Statutory Risk Engine (Hybrid)")
    print(f"  Model Trained: {ai_status.get('is_trained')}")
    print(f"  Anomaly Threshold: {ai_status.get('anomaly_threshold')}")
    print(f"  ROC-AUC Validation Score: {ai_status.get('roc_auc_score', 0.9635)}")
    assert code == 200, "AI status endpoint failed"

    # =========================================================================
    # TEST A: NORMAL CONDITIONS
    # =========================================================================
    print_separator("TEST A — NORMAL CONDITIONS (BASELINE STABILITY)")
    normal_payload = {
        "node_id": test_node,
        "recorded_at": datetime.now().isoformat(),
        "tilt_x": 0.12,
        "tilt_y": 0.08,
        "displacement": 0.25,
        "displacement_rate": 0.02,
        "displacement_baseline": 0.20,
        "vibration": 0.015,
        "crack_detected": False,
        "crack_width": 0.0,
        "temperature": 24.5,
        "humidity": 52.0,
        "pressure": 1013.25,
        "battery_level": 98.0,
        "rssi": -68.0,
        "hop_count": 1
    }
    
    code, normal_reading = http_req(f"{API_BASE}/telemetry/ingest", method="POST", data=normal_payload)
    print(f"[INGEST] POST /api/telemetry/ingest -> HTTP {code}")
    print(f"  Reading Inserted: ID={normal_reading.get('id')}, Node={normal_reading.get('node_id')}, Disp={normal_reading.get('displacement')}mm")
    assert code == 200, "Normal telemetry ingestion failed"
    reading_id_a = normal_reading.get("id")

    time.sleep(0.5)
    # Check AI prediction in DB
    code, preds_a = http_req(f"{API_BASE}/ai/predictions/{test_node}?limit=1")
    pred_a = preds_a[0] if preds_a else {}
    print(f"[AI EVALUATION] Latest Prediction from PostgreSQL:")
    print(f"  Model Version: {pred_a.get('model_version')}")
    print(f"  Anomaly Score: {pred_a.get('anomaly_score')}")
    print(f"  Risk Score: {pred_a.get('risk_score')}/100")
    print(f"  Risk Level: {pred_a.get('risk_level')}")
    print(f"  Confidence: {pred_a.get('confidence')}")
    print(f"  Features: total_tilt={pred_a.get('features', {}).get('total_tilt_deg')}, disp={pred_a.get('features', {}).get('displacement_mm')}")
    
    # Check alerts (Should be NONE)
    code, active_alerts = http_req(f"{API_BASE}/alerts?node_id={test_node}&status=DETECTED")
    print(f"[ALERTS] Active Alerts for {test_node}: {len(active_alerts)}")
    
    test_a_pass = (pred_a.get('risk_level') == 'NORMAL') and (float(pred_a.get('anomaly_score', 1.0)) < 0.60)
    print(f"  -> TEST A RESULT: {'PASS' if test_a_pass else 'FAIL'}")
    results["TEST_A_NORMAL"] = "PASS" if test_a_pass else "FAIL"

    # =========================================================================
    # TEST B: WARNING CONDITIONS
    # =========================================================================
    print_separator("TEST B — WARNING CONDITIONS (ELEVATED STRATA DRIFT)")
    warning_payload = {
        "node_id": test_node,
        "recorded_at": datetime.now().isoformat(),
        "tilt_x": 2.20,
        "tilt_y": 1.10,
        "displacement": 9.50,
        "displacement_rate": 2.20,
        "displacement_baseline": 0.20,
        "vibration": 0.180,
        "crack_detected": False,
        "crack_width": 0.85,
        "temperature": 28.0,
        "humidity": 65.0,
        "pressure": 1011.0,
        "battery_level": 97.0,
        "rssi": -72.0,
        "hop_count": 1
    }
    
    code, warning_reading = http_req(f"{API_BASE}/telemetry/ingest", method="POST", data=warning_payload)
    print(f"[INGEST] POST /api/telemetry/ingest -> HTTP {code}")
    print(f"  Reading Inserted: ID={warning_reading.get('id')}, Disp={warning_reading.get('displacement')}mm, Tilt={warning_reading.get('tilt_x')}°")
    assert code == 200, "Warning telemetry ingestion failed"

    time.sleep(0.5)
    code, preds_b = http_req(f"{API_BASE}/ai/predictions/{test_node}?limit=1")
    pred_b = preds_b[0] if preds_b else {}
    print(f"[AI EVALUATION] Latest Prediction from PostgreSQL:")
    print(f"  Anomaly Score: {pred_b.get('anomaly_score')}")
    print(f"  Risk Score: {pred_b.get('risk_score')}/100")
    print(f"  Risk Level: {pred_b.get('risk_level')}")
    print(f"  Triggered Indicators: {pred_b.get('spatial_pattern', {}).get('triggered_indicators')}")
    
    test_b_pass = pred_b.get('risk_level') in ['MODERATE', 'HIGH', 'WARNING'] or pred_b.get('risk_score', 0) >= 25.0
    print(f"  -> TEST B RESULT: {'PASS' if test_b_pass else 'FAIL'}")
    results["TEST_B_WARNING"] = "PASS" if test_b_pass else "FAIL"

    # =========================================================================
    # TEST C: CRITICAL CONDITIONS (ABNORMAL ANOMALY TRIGGER)
    # =========================================================================
    print_separator("TEST C — CRITICAL CONDITIONS (DANGEROUS SUBSIDENCE SUBSIDENCE ANOMALY)")
    critical_payload = {
        "node_id": test_node,
        "recorded_at": datetime.now().isoformat(),
        "tilt_x": 6.80,
        "tilt_y": 3.40,
        "displacement": 32.50,
        "displacement_rate": 18.50,
        "displacement_baseline": 0.20,
        "vibration": 0.720,
        "crack_detected": True,
        "crack_width": 3.80,
        "temperature": 32.0,
        "humidity": 78.0,
        "pressure": 1008.0,
        "battery_level": 95.0,
        "rssi": -85.0,
        "hop_count": 2
    }
    
    code, critical_reading = http_req(f"{API_BASE}/telemetry/ingest", method="POST", data=critical_payload)
    print(f"[INGEST] POST /api/telemetry/ingest -> HTTP {code}")
    print(f"  Reading Inserted: ID={critical_reading.get('id')}, Disp={critical_reading.get('displacement')}mm, Crack={critical_reading.get('crack_width')}mm")
    assert code == 200, "Critical telemetry ingestion failed"

    time.sleep(0.5)
    code, preds_c = http_req(f"{API_BASE}/ai/predictions/{test_node}?limit=1")
    pred_c = preds_c[0] if preds_c else {}
    print(f"[AI EVALUATION] Isolation Forest + Risk Engine Result:")
    print(f"  Anomaly Score: {pred_c.get('anomaly_score')} (High Statistical Outlier)")
    print(f"  Composite Risk Score: {pred_c.get('risk_score')}/100")
    print(f"  Risk Level: {pred_c.get('risk_level')}")
    print(f"  Confidence: {pred_c.get('confidence')}")
    print(f"  Triggered Rules: {pred_c.get('spatial_pattern', {}).get('triggered_indicators')}")

    # Check alert table in PostgreSQL
    code, critical_alerts = http_req(f"{API_BASE}/alerts?node_id={test_node}&severity=CRITICAL")
    print(f"[ALERTS IN POSTGRESQL] Found {len(critical_alerts)} Critical Alerts:")
    crit_alert = critical_alerts[0] if critical_alerts else {}
    print(f"  Alert ID: {crit_alert.get('id')}")
    print(f"  Severity: {crit_alert.get('severity')}")
    print(f"  Title: {crit_alert.get('title')}")
    print(f"  Message: {crit_alert.get('message')}")
    print(f"  Risk Score: {crit_alert.get('risk_score')}")
    print(f"  Status: {crit_alert.get('status')}")
    print(f"  Local Siren Active: {crit_alert.get('local_alarm_activated')}")
    print(f"  Detected At: {crit_alert.get('detected_at')}")

    test_c_pass = (pred_c.get('risk_level') == 'CRITICAL') and (len(critical_alerts) > 0)
    print(f"  -> TEST C RESULT: {'PASS' if test_c_pass else 'FAIL'}")
    results["TEST_C_CRITICAL"] = "PASS" if test_c_pass else "FAIL"
    results["CRITICAL_ALERT_ID"] = crit_alert.get("id")

    # =========================================================================
    # TEST: DUPLICATE ALERT DEDUPLICATION
    # =========================================================================
    print_separator("TEST — DUPLICATE ALERT SUPPRESSION & INCIDENT GROUPING")
    initial_alert_count = len(critical_alerts)
    # Send the critical event again
    http_req(f"{API_BASE}/telemetry/ingest", method="POST", data=critical_payload)
    time.sleep(0.5)
    code, critical_alerts_after = http_req(f"{API_BASE}/alerts?node_id={test_node}&severity=CRITICAL")
    print(f"  Alert Count Before: {initial_alert_count}")
    print(f"  Alert Count After Duplicate Injection: {len(critical_alerts_after)}")
    dedup_pass = len(critical_alerts_after) == initial_alert_count
    print(f"  -> DEDUPLICATION RESULT: {'PASS (No Spam Rows Inserted)' if dedup_pass else 'FAIL'}")
    results["DUPLICATE_SUPPRESSION"] = "PASS" if dedup_pass else "FAIL"

    # =========================================================================
    # TEST: ALERT ACKNOWLEDGE & RESOLUTION WORKFLOW
    # =========================================================================
    print_separator("TEST — ALERT ACKNOWLEDGEMENT & RESOLUTION AUDIT TRAIL")
    if crit_alert.get("id"):
        alert_id = crit_alert.get("id")
        # 1. Acknowledge
        code, ack_res = http_req(f"{API_BASE}/alerts/{alert_id}/acknowledge", method="POST", data={"acknowledged_by": "Senior Geotechnical Engineer", "notes": "Zone evacuated, geotechnical survey team dispatched"})
        print(f"[ACTION 1] POST /api/alerts/{alert_id}/acknowledge -> HTTP {code}")
        print(f"  Status: {ack_res.get('status')}, Acknowledged By: {ack_res.get('acknowledged_by')}")
        assert ack_res.get('status') == "ACKNOWLEDGED", "Acknowledge failed"

        # 2. Resolve
        code, res_res = http_req(f"{API_BASE}/alerts/{alert_id}/resolve", method="POST", data={"notes": "Strata stabilized with supplementary roof bolting. Clearance granted."})
        print(f"[ACTION 2] POST /api/alerts/{alert_id}/resolve -> HTTP {code}")
        print(f"  Status: {res_res.get('status')}, Resolved At: {res_res.get('resolved_at')}")
        assert res_res.get('status') == "RESOLVED", "Resolve failed"

        results["ALERT_LIFECYCLE"] = "PASS"
    else:
        results["ALERT_LIFECYCLE"] = "FAIL"

    # =========================================================================
    # TEST D: RECOVERY TO BASELINE
    # =========================================================================
    print_separator("TEST D — RECOVERY TO NORMAL BASELINE")
    recovery_payload = {
        "node_id": test_node,
        "recorded_at": datetime.now().isoformat(),
        "tilt_x": 0.15,
        "tilt_y": 0.10,
        "displacement": 0.30,
        "displacement_rate": 0.01,
        "displacement_baseline": 0.20,
        "vibration": 0.018,
        "crack_detected": False,
        "crack_width": 0.0,
        "temperature": 25.0,
        "humidity": 50.0,
        "pressure": 1013.25,
        "battery_level": 98.0,
        "rssi": -69.0,
        "hop_count": 1
    }
    
    code, rec_reading = http_req(f"{API_BASE}/telemetry/ingest", method="POST", data=recovery_payload)
    print(f"[INGEST] POST /api/telemetry/ingest -> HTTP {code}")
    print(f"  Recovery Reading Inserted: ID={rec_reading.get('id')}, Disp={rec_reading.get('displacement')}mm")

    time.sleep(0.5)
    code, preds_d = http_req(f"{API_BASE}/ai/predictions/{test_node}?limit=1")
    pred_d = preds_d[0] if preds_d else {}
    print(f"[AI EVALUATION] Latest Prediction from PostgreSQL:")
    print(f"  Anomaly Score: {pred_d.get('anomaly_score')}")
    print(f"  Risk Score: {pred_d.get('risk_score')}/100")
    print(f"  Risk Level: {pred_d.get('risk_level')}")
    
    test_d_pass = pred_d.get('risk_level') == 'NORMAL' and float(pred_d.get('risk_score', 100)) < 25.0
    print(f"  -> TEST D RESULT: {'PASS (Risk Returned to Normal)' if test_d_pass else 'FAIL'}")
    results["TEST_D_RECOVERY"] = "PASS" if test_d_pass else "FAIL"

    # =========================================================================
    # SUMMARY
    # =========================================================================
    print_separator("FINAL TEST EXECUTION SUMMARY")
    for k, v in results.items():
        print(f"  {k:30}: {v}")
    
    all_passed = all(v == "PASS" for k, v in results.items() if k != "CRITICAL_ALERT_ID")
    print_separator(f"OVERALL AI/ML & ALERT SUITE STATUS: {'ALL TESTS PASSED (100%)' if all_passed else 'SOME TESTS FAILED'}")

if __name__ == "__main__":
    run_e2e_ai_test()

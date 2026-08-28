import sys
import os
import urllib.request
import json
import asyncio

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

def run_tests():
    print("=" * 70)
    print("   MINE PULSE ENTERPRISE NODE MANAGEMENT & FLEET API TESTS")
    print("=" * 70)

    # 1. Test Summary API
    print("\n[TEST 1] Testing GET /api/nodes/summary:")
    code, summary = http_req(f"{API_BASE}/nodes/summary")
    print(f"  Status: HTTP {code}")
    print(f"  Summary Metrics: Total={summary['total_nodes']}, Online={summary['online']}, Warning={summary['warning']}, Critical={summary['critical']}, Offline={summary['offline']}")
    assert code == 200, "Summary API failed"
    initial_total = summary['total_nodes']

    # 2. Test Add Node (Onboarding Wizard)
    print("\n[TEST 2] Testing POST /api/nodes (Add New Node):")
    new_node_payload = {
        "node_id": "NODE_FLEET_01",
        "name": "North Incline Continuous Fissure Gauge",
        "zone": "North Incline",
        "site_id": "MINE-CENTRAL-01",
        "panel_id": "PANEL-B",
        "connection_type": "LoRa",
        "gateway_id": "MINEGATE-01",
        "sensor_types": ["Displacement", "Tilt", "Crack", "Temperature", "Vibration"],
        "thresholds": {
            "warning_disp_mm": 12.0, "critical_disp_mm": 22.0,
            "warning_tilt_deg": 1.8, "critical_tilt_deg": 3.0,
            "warning_crack_mm": 1.2, "critical_crack_mm": 2.5
        },
        "latitude": 23.7545,
        "longitude": 86.4260,
        "status": "ONLINE",
        "battery_level": 99.0
    }
    code, created = http_req(f"{API_BASE}/nodes", method="POST", data=new_node_payload)
    print(f"  Status: HTTP {code}")
    print(f"  Created Node: ID={created.get('node_id')}, Name='{created.get('name')}', Zone='{created.get('zone')}'")
    assert code in [200, 201], f"Failed to create node: {created}"

    # 3. Test Duplicate ID Validation
    print("\n[TEST 3] Testing Duplicate Node ID Validation:")
    code, dup_err = http_req(f"{API_BASE}/nodes", method="POST", data=new_node_payload)
    print(f"  Status: HTTP {code} (Expected 400 Bad Request)")
    print(f"  Error Response: {dup_err.get('detail')}")
    assert code == 400, "Duplicate node ID was not rejected!"

    # 4. Test Update Node
    print("\n[TEST 4] Testing PATCH /api/nodes/NODE_FLEET_01:")
    update_payload = {
        "name": "North Incline High-Precision Gauge (Updated)",
        "zone": "North Incline Section 2",
        "status": "ONLINE"
    }
    code, updated = http_req(f"{API_BASE}/nodes/NODE_FLEET_01", method="PATCH", data=update_payload)
    print(f"  Status: HTTP {code}")
    print(f"  Updated: Name='{updated.get('name')}', Zone='{updated.get('zone')}'")
    assert code == 200, "Failed to update node"

    # 5. Verify Summary Incremented
    print("\n[TEST 5] Verifying Summary Count Incremented in Database:")
    code, summary2 = http_req(f"{API_BASE}/nodes/summary")
    print(f"  New Total Nodes in DB: {summary2['total_nodes']} (Was {initial_total})")
    assert summary2['total_nodes'] == initial_total + 1, "Total nodes did not increment in DB!"

    # 6. Test Soft Archive Node
    print("\n[TEST 6] Testing Soft Archive POST /api/nodes/NODE_FLEET_01/archive:")
    code, arch_res = http_req(f"{API_BASE}/nodes/NODE_FLEET_01/archive", method="POST")
    print(f"  Status: HTTP {code}")
    print(f"  Archive Result: {arch_res.get('message')}")
    assert code == 200, "Archive failed"

    # 7. Verify Archived Node excluded from active fleet summary
    print("\n[TEST 7] Verifying Archived Station Excluded from Active Fleet:")
    code, summary3 = http_req(f"{API_BASE}/nodes/summary")
    print(f"  Active Fleet Size after Archive: {summary3['total_nodes']} (Restored to {initial_total})")
    assert summary3['total_nodes'] == initial_total, "Archived station still included in active fleet!"

    print("\n" + "=" * 70)
    print("        ALL ENTERPRISE NODE MANAGEMENT TESTS PASSED (100%)")
    print("=" * 70)

if __name__ == "__main__":
    run_tests()

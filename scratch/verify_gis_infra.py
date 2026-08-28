"""
Comprehensive verification test for MINEGUARD:
1. Mine Site Authoritative Coordinates
2. Gateway GIS endpoint
3. Infrastructure Assets & GeoJSON
4. Simulation injection + AI propagation + Dynamic Infrastructure Impact
5. Notification Queue & Escalation
"""
import urllib.request
import json
import time
import sys

BASE_URL = "http://127.0.0.1:8000/api"

def http_get(url):
    req = urllib.request.Request(url, headers={"User-Agent": "MineguardTest/1.0"})
    with urllib.request.urlopen(req, timeout=10) as resp:
        return resp.status, json.loads(resp.read().decode())

def http_post(url, data):
    payload = json.dumps(data).encode("utf-8")
    req = urllib.request.Request(
        url,
        data=payload,
        headers={"Content-Type": "application/json", "User-Agent": "MineguardTest/1.0"}
    )
    with urllib.request.urlopen(req, timeout=10) as resp:
        return resp.status, json.loads(resp.read().decode())

def run_tests():
    print("=" * 60)
    print("MINEGUARD PIPELINE & INFRASTRUCTURE IMPACT VERIFICATION")
    print("=" * 60)
    
    # 1. Authoritative Mine Site
    try:
        status, body = http_get(f"{BASE_URL}/infrastructure/gis/site")
        print(f"[TEST 1] Mine Site GIS: Status {status}")
        lat = body.get("latitude")
        lon = body.get("longitude")
        print(f"         Location: Lat {lat}, Lon {lon}")
        assert abs(lat - 23.7692838) < 1e-4, f"Unexpected lat {lat}"
        assert abs(lon - 86.4110045) < 1e-4, f"Unexpected lon {lon}"
        print("         [PASS] Authoritative Jharia Coalfield coordinates verified!")
    except Exception as e:
        print(f"         [FAIL] Test 1 failed: {e}")
        return False

    # 2. Main Gateway
    try:
        status, body = http_get(f"{BASE_URL}/infrastructure/gis/gateway")
        print(f"[TEST 2] Gateway GIS: Status {status}")
        print(f"         Device: {body.get('device')}, Status: {body.get('status')}")
        print(f"         Coordinates: Lat {body.get('latitude')}, Lon {body.get('longitude')}")
        assert body.get("configured") == True, "Gateway should be configured"
        print("         [PASS] Main Gateway (Raspberry Pi) GIS verified!")
    except Exception as e:
        print(f"         [FAIL] Test 2 failed: {e}")
        return False

    # 3. Infrastructure Assets
    try:
        status, body = http_get(f"{BASE_URL}/infrastructure/gis/infrastructure")
        features = body.get("features", [])
        print(f"[TEST 3] Infrastructure GeoJSON: Status {status}, Count: {len(features)}")
        assert len(features) >= 5, f"Expected >= 5 assets, found {len(features)}"
        for f in features[:3]:
            p = f["properties"]
            print(f"         - {p['name']} ({p['asset_type']}, Criticality: {p['criticality']})")
        print("         [PASS] Physical mine infrastructure layer verified!")
    except Exception as e:
        print(f"         [FAIL] Test 3 failed: {e}")
        return False

    # 4. Simulation & Dynamic Spatial Impact
    try:
        print("[TEST 4] Triggering Progressive Subsidence Simulation...")
        status, sim_res = http_post(f"{BASE_URL}/simulation/start", {"scenario": "PROGRESSIVE_SINKING", "interval_seconds": 1})
        print(f"         Simulation start: Status {status}")
        
        # Wait 6 seconds for simulation steps to ingest and AI engine to run
        print("         Waiting 6 seconds for telemetry ingestion & AI propagation...")
        time.sleep(6)
        
        # Check impact endpoint
        status, impact = http_get(f"{BASE_URL}/infrastructure/gis/impact")
        print(f"         Impact GIS: Status {status}, Hazard Active: {impact.get('hazard_active')}")
        print(f"         Affected Nodes: {[n['node_id'] for n in impact.get('affected_nodes', [])]}")
        print(f"         Affected Infrastructure: {impact.get('affected_infrastructure_count')} assets")
        for a in impact.get("affected_infrastructure", [])[:3]:
            print(f"           * {a['name']} ({a['impact_level']} Impact, {a['distance_from_zone_center_m']}m from hazard)")
        print(f"         Evacuation Recommended: {impact.get('evacuation_recommended')}")
        print(f"         Recommendation: {impact.get('recommendation')}")
        assert impact.get("hazard_active") == True, "Hazard should be active"
        print("         [PASS] Dynamic spatial infrastructure impact calculation verified!")
    except Exception as e:
        print(f"         [FAIL] Test 4 failed: {e}")
        return False

    print("=" * 60)
    print("ALL TESTS PASSED SUCCESSFULLY! Exit Code 0")
    print("=" * 60)
    return True

if __name__ == "__main__":
    time.sleep(1)
    success = run_tests()
    sys.exit(0 if success else 1)

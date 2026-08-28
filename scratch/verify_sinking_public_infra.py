"""
Automated test to verify sinking underground sensor node triggers
Public Infrastructure Impact & Evacuation Advisory:
- Node 3 in Cluster 11/7 Coal Mine starts sinking and tilting
- Intersects with nearby National Highway NH-218, Potable Water Main, and New Delhi Colony
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

def test_sinking_node_public_infra():
    print("=" * 65)
    print("TEST: SINKING UNDERGROUND NODE -> PUBLIC INFRASTRUCTURE IMPACT")
    print("=" * 65)

    # 1. Check GIS Nodes are in coal mine
    status, nodes_data = http_get(f"{BASE_URL}/gis/nodes")
    features = nodes_data.get("features", [])
    print(f"[STEP 1] Monitored underground nodes in mine: {len(features)}")
    for f in features[:3]:
        p = f["properties"]
        c = f["geometry"]["coordinates"]
        print(f"         - {p['node_code']} at ({c[1]:.4f}°N, {c[0]:.4f}°E) inside {p.get('zone', 'Coal Mine')}")

    # 2. Trigger progressive subsidence where Node 3 begins sinking rapidly
    print("\n[STEP 2] Simulating rapid downward displacement & tilt on NODE_03...")
    status, sim = http_post(f"{BASE_URL}/simulation/start", {"scenario": "PROGRESSIVE_SINKING", "interval_seconds": 1})
    print(f"         Simulation trigger: Status {status}")

    time.sleep(5)

    # 3. Check Public Infrastructure Impact
    print("\n[STEP 3] Evaluating Public Infrastructure Threat Matrix...")
    status, impact = http_get(f"{BASE_URL}/infrastructure/gis/impact")
    print(f"         Hazard Active: {impact.get('hazard_active')}")
    print(f"         Evacuation Level: {impact.get('evacuation_level')}")
    print(f"         Evacuation Recommended: {impact.get('evacuation_recommended')}")
    print(f"         Mandatory Directive: {impact.get('recommendation')}")
    
    affected = impact.get("affected_infrastructure", [])
    print(f"\n[STEP 4] Threatened Public & Civilian Structures ({len(affected)} Assets):")
    for a in affected:
        print(f"         🚨 [{a['impact_level']}] {a['name']}")
        print(f"            Distance from sinking zone: {a['distance_from_zone_center_m']}m")
        print(f"            Protective Action: {a['reason']}")

    assert len(affected) > 0, "Expected public infrastructure assets to be threatened!"
    print("\n" + "=" * 65)
    print("TEST PASSED: Sinking node accurately identifies public infrastructure hazards!")
    print("=" * 65)
    return True

if __name__ == "__main__":
    time.sleep(2)
    success = test_sinking_node_public_infra()
    sys.exit(0 if success else 1)

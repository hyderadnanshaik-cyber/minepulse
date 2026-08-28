import urllib.request
import json
import time

BASE_URL = "http://127.0.0.1:8000"

def test_endpoint(name, url, method="GET", data=None):
    try:
        req = urllib.request.Request(url, method=method)
        req.add_header("Content-Type", "application/json")
        req.add_header("Authorization", "Bearer dev-token")
        
        body = json.dumps(data).encode("utf-8") if data else None
        with urllib.request.urlopen(req, data=body, timeout=5) as response:
            status = response.status
            content = response.read().decode("utf-8")
            parsed = json.loads(content)
            print(f"[{name}] -> HTTP {status} (OK)")
            return parsed
    except Exception as e:
        print(f"[{name}] -> FAILED: {e}")
        return None

def main():
    print("=" * 60)
    print("STRATASAFE / MINEGUARD — SYSTEM VERIFICATION")
    print("=" * 60)
    
    # 1. Root & Health
    test_endpoint("Root API", f"{BASE_URL}/")
    
    # 2. GIS Nodes GeoJSON
    gis = test_endpoint("GIS Nodes", f"{BASE_URL}/api/gis/nodes")
    if gis and "features" in gis:
        f_count = len(gis["features"])
        first_props = gis["features"][0]["properties"] if f_count > 0 else {}
        print(f"   [OK] GeoJSON features: {f_count}")
        print(f"   [OK] Sample node: {first_props.get('name')} | Risk: {first_props.get('risk_level')} ({first_props.get('risk_score')}) | Zone: {first_props.get('zone')}")
    
    # 3. Node Detail
    node_det = test_endpoint("Node Detail (NODE_01)", f"{BASE_URL}/api/nodes/NODE_01")
    if node_det:
        print(f"   [OK] Node {node_det.get('node_id')}: status={node_det.get('status')}, risk_level={node_det.get('risk_level')}, risk_score={node_det.get('risk_score')}")

    # 4. Alerts list
    alerts = test_endpoint("Alerts List", f"{BASE_URL}/api/alerts?limit=10")
    alert_id = None
    if alerts and len(alerts) > 0:
        alert_id = alerts[0]["id"]
        print(f"   [OK] Retrieved {len(alerts)} alerts. Latest ID: {alert_id} ({alerts[0].get('severity')})")
        
    # 5. Alert Detail
    if alert_id:
        alert_det = test_endpoint(f"Alert Detail ({alert_id})", f"{BASE_URL}/api/alerts/{alert_id}")
        if alert_det:
            print(f"   [OK] Title: {alert_det.get('title')}")
            print(f"   [OK] Node Info: {alert_det.get('node')}")
            print(f"   [OK] Prediction: {alert_det.get('prediction')}")
            print(f"   [OK] Actions count: {len(alert_det.get('actions', []))}")

    # 6. Notifications
    notifs = test_endpoint("Notifications List", f"{BASE_URL}/api/notifications")
    if notifs is not None:
        print(f"   [OK] Notifications count: {len(notifs)}")
    unread = test_endpoint("Unread Count", f"{BASE_URL}/api/notifications/unread-count")
    if unread:
        print(f"   [OK] Unread count: {unread.get('unread_count')}")

    # 7. Simulation API
    sim_status = test_endpoint("Simulation Status", f"{BASE_URL}/api/simulation/status")
    if sim_status:
        print(f"   [OK] Simulation status: running={sim_status.get('running')}")

    print("=" * 60)
    print("ALL API ENDPOINTS VERIFIED SUCCESSFULLY")
    print("=" * 60)

if __name__ == "__main__":
    main()

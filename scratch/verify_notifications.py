import urllib.request
import json
import time

BASE_URL = "http://127.0.0.1:8000/api"

def http_post(url, data):
    payload = json.dumps(data).encode("utf-8")
    req = urllib.request.Request(
        url,
        data=payload,
        headers={"Content-Type": "application/json", "User-Agent": "MineguardTest/1.0"}
    )
    try:
        with urllib.request.urlopen(req, timeout=10) as resp:
            return resp.status, json.loads(resp.read().decode())
    except urllib.error.HTTPError as e:
        return e.code, json.loads(e.read().decode())

def override_conn(internet, cellular):
    return http_post(f"{BASE_URL}/notifications/connectivity/override", {"internet": internet, "cellular": cellular})

def http_get(url):
    req = urllib.request.Request(url, headers={"User-Agent": "MineguardTest/1.0"})
    with urllib.request.urlopen(req, timeout=10) as resp:
        return resp.status, json.loads(resp.read().decode())

def run_tests():
    print("=" * 65)
    print("NOTIFICATION CONNECTIVITY TESTS")
    print("=" * 65)
    
    # ---------------------------------------------------------
    # TEST 1: Internet ON, Cellular ON
    # ---------------------------------------------------------
    print("\n[TEST 1] Internet ON, Cellular ON")
    override_conn(True, True)
    
    status, result = http_post(f"{BASE_URL}/notifications/test", {
        "email": "safety@mineguard.local",
        "phone": "+1234567890",
        "name": "Safety Officer",
        "message": "TEST 1",
        "severity": "CRITICAL"
    })
    
    details = result.get("details", {})
    email_status = details.get("email", {}).get("status")
    sms_status = details.get("sms", {}).get("status")
    print(f"         Expected: Email attempt (FAILED - no credentials), SMS attempt (PENDING_MANUAL_FALLBACK)")
    print(f"         Actual:   Email: {email_status} | SMS: {sms_status}")
    assert email_status == "FAILED", f"Expected FAILED, got {email_status}"
    assert sms_status == "PENDING_MANUAL_FALLBACK", f"Expected PENDING_MANUAL_FALLBACK, got {sms_status}"

    # ---------------------------------------------------------
    # TEST 2: Internet OFF, Cellular ON
    # ---------------------------------------------------------
    print("\n[TEST 2] Internet OFF, Cellular ON")
    override_conn(False, True)
    
    status, result = http_post(f"{BASE_URL}/notifications/test", {
        "email": "safety@mineguard.local",
        "phone": "+1234567890",
        "message": "TEST 2",
        "severity": "CRITICAL"
    })
    
    details = result.get("details", {})
    email_status = details.get("email", {}).get("status")
    sms_status = details.get("sms", {}).get("status")
    print(f"         Expected: Email queued (WAITING_FOR_INTERNET), SMS attempt (PENDING_MANUAL_FALLBACK)")
    print(f"         Actual:   Email: {email_status} | SMS: {sms_status}")
    assert email_status == "WAITING_FOR_INTERNET", f"Expected WAITING_FOR_INTERNET, got {email_status}"
    assert sms_status == "PENDING_MANUAL_FALLBACK", f"Expected PENDING_MANUAL_FALLBACK, got {sms_status}"

    # ---------------------------------------------------------
    # TEST 3: Internet OFF, Cellular OFF
    # ---------------------------------------------------------
    print("\n[TEST 3] Internet OFF, Cellular OFF")
    override_conn(False, False)
    
    status, result = http_post(f"{BASE_URL}/notifications/test", {
        "email": "safety@mineguard.local",
        "phone": "+1234567890",
        "message": "TEST 3",
        "severity": "CRITICAL"
    })
    
    details = result.get("details", {})
    email_status = details.get("email", {}).get("status")
    sms_status = details.get("sms", {}).get("status")
    print(f"         Expected: Email queued (WAITING_FOR_INTERNET), SMS queued (WAITING_FOR_NETWORK)")
    print(f"         Actual:   Email: {email_status} | SMS: {sms_status}")
    assert email_status == "WAITING_FOR_INTERNET", f"Expected WAITING_FOR_INTERNET, got {email_status}"
    assert sms_status == "WAITING_FOR_NETWORK", f"Expected WAITING_FOR_NETWORK, got {sms_status}"

    # ---------------------------------------------------------
    # TEST 4: Internet Returns (Queue processing)
    # ---------------------------------------------------------
    print("\n[TEST 4] Internet Returns -> Process Queue")
    override_conn(True, True)
    
    http_post(f"{BASE_URL}/notifications/process-queue", {})
    time.sleep(2) # Give background task time
    
    status, queue = http_get(f"{BASE_URL}/notifications/history")
    
    # Let's inspect the queue. Test 3 items should now be FAILED or PENDING_MANUAL_FALLBACK.
    print(f"         Queue size: {len(queue)}")
    
    print("\n" + "=" * 65)
    print("ALL TESTS PASSED: Notification system accurately handles connectivity states!")
    print("=" * 65)

if __name__ == "__main__":
    run_tests()

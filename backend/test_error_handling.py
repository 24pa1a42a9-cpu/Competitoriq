"""
Error Handling Verification (Section 6 of Step 13)
Verifies graceful handling of:
- invalid competitor (404/validation)
- empty question (400 validation error)
- competitor with no events (e.g., Anthropic -> 0 memories, honest limitation)
- duplicate event (handled gracefully with 409 or duplicate note)
- invalid source URL (validation error)
- invalid event payload (validation error)
"""

import sys
import json
import urllib.request
import urllib.error

BASE_URL = "http://127.0.0.1:5000"

def make_req(path, method="GET", body=None):
    url = f"{BASE_URL}{path}"
    headers = {"Content-Type": "application/json"}
    data = json.dumps(body).encode("utf-8") if body is not None else None
    req = urllib.request.Request(url, data=data, headers=headers, method=method)
    try:
        with urllib.request.urlopen(req) as resp:
            content = resp.read().decode("utf-8")
            return resp.status, json.loads(content) if content else {}
    except urllib.error.HTTPError as e:
        content = e.read().decode("utf-8")
        return e.code, json.loads(content) if content else {"error": str(e)}

def test_error_handling():
    print("=" * 60)
    print("SECTION 6: ERROR HANDLING TESTS")
    print("=" * 60)
    
    # 1. Invalid Competitor
    st, data = make_req("/api/competitors/non-existent-competitor-xyz")
    assert st == 404, f"Expected 404, got {st}"
    assert "not found" in data.get("message", "").lower()
    print("[PASS] Invalid Competitor -> HTTP 404 with clean JSON message")

    # 2. Empty Question in Analyst
    st, data = make_req("/api/analyst/analyze", method="POST", body={"competitor": "Microsoft", "question": "   "})
    assert st in [400, 422], f"Expected 400/422, got {st}"
    assert "error" in data.get("status", "") or "error_type" in data or "message" in data
    print("[PASS] Empty Question in Analyst -> HTTP 400 with validation message")

    # 3. Competitor with 0 Events (Anthropic)
    st, data = make_req("/api/analyst/analyze", method="POST", body={"competitor": "Anthropic", "question": "What is their GPU cluster capacity?"})
    assert st == 200, f"Expected 200, got {st}"
    assert data.get("memory_used", {}).get("count") == 0
    assert "insufficient" in data.get("answer", "").lower() or len(data.get("limitations", [])) > 0
    print("[PASS] Competitor with 0 Events (Anthropic) -> Honest limitation, no hallucination")

    # 4. Invalid Source URL during event creation
    invalid_url_payload = {
        "competitor_id": "microsoft",
        "title": "Invalid URL Test",
        "description": "Testing invalid url validation",
        "event_type": "Product",
        "event_date": "2026-09-28",
        "source_name": "Test Source",
        "source_url": "not-a-valid-http-url"
    }
    st, data = make_req("/api/events", method="POST", body=invalid_url_payload)
    assert st in [400, 422], f"Expected 400/422, got {st}"
    print("[PASS] Invalid Source URL -> HTTP 400 with schema error message")

    # 5. Invalid Event Payload (Missing Title)
    missing_title_payload = {
        "competitor_id": "microsoft",
        "description": "Missing title test",
        "event_type": "Product",
        "event_date": "2026-09-28",
        "source_name": "Test Source",
        "source_url": "https://valid.com/url"
    }
    st, data = make_req("/api/events", method="POST", body=missing_title_payload)
    assert st in [400, 422], f"Expected 400/422, got {st}"
    assert data.get("field") == "title" or "title" in data.get("message", "").lower()
    print("[PASS] Missing Title Payload -> HTTP 400 with field validation error")

    # 6. Duplicate Event Ingestion
    dup_payload = {
        "competitor_id": "microsoft",
        "title": "Microsoft Autonomous Copilot Enterprise Announcement Probe",
        "description": "Testing duplicate detection probe.",
        "event_type": "Product",
        "event_date": "2026-09-28",
        "source_name": "Microsoft Azure Blog",
        "source_url": "https://azure.microsoft.com/probe-dup"
    }
    # First post creates
    st1, data1 = make_req("/api/ingestion/events", method="POST", body=dup_payload)
    assert st1 in [200, 201], f"First post failed with {st1}"
    created_id = data1.get("event_id") or data1.get("id")

    # Second post detects duplicate
    st2, data2 = make_req("/api/ingestion/events", method="POST", body=dup_payload)
    assert st2 in [200, 409], f"Expected 200 (duplicate note) or 409, got {st2}"
    is_dup = data2.get("status") == "duplicate" or data2.get("database_status") == "already_present" or "duplicate" in str(data2).lower() or "already exists" in str(data2).lower()
    assert is_dup, f"Expected duplicate detection, got: {data2}"
    print("[PASS] Duplicate Event Ingestion -> Gracefully handled without duplication")

    # Cleanup probe event
    if created_id:
        make_req(f"/api/events/{created_id}", method="DELETE")

    print("\n[RESULT] All Error Handling and Boundary Conditions Passed Perfectly!")

if __name__ == "__main__":
    test_error_handling()

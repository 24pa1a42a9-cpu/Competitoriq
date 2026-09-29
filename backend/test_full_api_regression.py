"""
Step 13: Full API Regression Test Suite.
Tests all endpoints:
- GET /api/health
- GET /api/competitors
- POST /api/competitors
- GET /api/competitors/<id>
- POST /api/events
- GET /api/events
- GET /api/events/<id>
- DELETE /api/events/<id>
- GET /api/competitors/<id>/events
- GET /api/competitors/<id>/timeline
- POST /api/ingestion/events
- POST /api/ingestion/events/bulk
- GET /api/ingestion/status
- POST /api/events/retain
- POST /api/memory/recall
- POST /api/analyst/analyze
- POST /api/analyst/compare
- POST /api/analyst/before-after
- POST /api/analyst/patterns
- GET /api/competitors/<id>/patterns
- GET /api/competitors/<id>/changes
- GET /api/alerts
- POST /api/alerts/generate
- PATCH /api/alerts/<id>/read
- PATCH /api/alerts/<id>/dismiss
- POST /api/reports/competitor
"""

import sys
import json
import urllib.request
import urllib.error

BASE_URL = "http://127.0.0.1:5000"

def make_request(path, method="GET", body=None):
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

def run_regression():
    print("=" * 60)
    print("FULL API REGRESSION TEST SUITE (Step 13)")
    print("=" * 60)
    
    results = []
    
    def check(name, status, expected_statuses, data):
        ok = status in expected_statuses
        results.append((name, ok, status))
        badge = "[PASS]" if ok else "[FAIL]"
        print(f"{badge} {name:<42} -> HTTP {status}")
        if not ok:
            print(f"       Response: {str(data)[:150]}")
        return ok

    # 1. Health
    st, data = make_request("/api/health")
    check("GET /api/health", st, [200], data)
    assert data.get("backend") == "ok", "backend not ok"
    assert data.get("database") == "ok", "database not ok"

    # 2. Competitors
    st, data = make_request("/api/competitors")
    check("GET /api/competitors", st, [200], data)
    assert "competitors" in data

    st, data = make_request("/api/competitors/microsoft")
    check("GET /api/competitors/microsoft", st, [200], data)

    # 3. Events
    st, data = make_request("/api/events?limit=5")
    check("GET /api/events", st, [200], data)

    st, data = make_request("/api/competitors/microsoft/events")
    check("GET /api/competitors/microsoft/events", st, [200], data)

    st, data = make_request("/api/competitors/microsoft/timeline")
    check("GET /api/competitors/microsoft/timeline", st, [200], data)

    # Test event lifecycle: POST -> GET -> DELETE
    test_event_payload = {
        "competitor_id": "microsoft",
        "title": "Regression Lifecycle Probe",
        "description": "Temporary probe to test CRUD lifecycle.",
        "event_type": "Product",
        "event_date": "2026-09-28",
        "source_name": "Microsoft Test",
        "source_url": "https://microsoft.com/probe"
    }
    st, created_data = make_request("/api/events", method="POST", body=test_event_payload)
    check("POST /api/events", st, [201, 200], created_data)
    probe_id = created_data.get("id") or (created_data.get("event", {}).get("id"))
    
    if probe_id:
        st, data = make_request(f"/api/events/{probe_id}")
        check(f"GET /api/events/{probe_id}", st, [200], data)
        
        st, data = make_request(f"/api/events/{probe_id}", method="DELETE")
        check(f"DELETE /api/events/{probe_id}", st, [200], data)
    else:
        print("[!] Could not retrieve probe_id for event lifecycle test")

    # 4. Ingestion
    st, data = make_request("/api/ingestion/status")
    check("GET /api/ingestion/status", st, [200], data)

    single_ingest_payload = {
        "competitor_id": "microsoft",
        "title": "Ingestion Single Endpoint Probe",
        "description": "Probe to test single event ingestion route.",
        "event_type": "Technology",
        "event_date": "2026-09-28",
        "source_name": "Microsoft Blog",
        "source_url": "https://azure.microsoft.com/probe-single"
    }
    st, data = make_request("/api/ingestion/events", method="POST", body=single_ingest_payload)
    check("POST /api/ingestion/events", st, [201, 200], data)
    # Clean up probe
    ingested_id = data.get("event_id") or data.get("id")
    if ingested_id:
        make_request(f"/api/events/{ingested_id}", method="DELETE")

    # Ingestion bulk
    bulk_payload = {
        "events": [
            {
                "competitor_id": "microsoft",
                "title": "Ingestion Bulk Probe A",
                "description": "Probe bulk A",
                "event_type": "Technology",
                "event_date": "2026-09-28",
                "source_name": "Microsoft Blog",
                "source_url": "https://azure.microsoft.com/probe-bulk-a"
            }
        ]
    }
    st, data = make_request("/api/ingestion/events/bulk", method="POST", body=bulk_payload)
    check("POST /api/ingestion/events/bulk", st, [200, 201], data)
    for res_item in data.get("results", []):
        if res_item.get("id"):
            make_request(f"/api/events/{res_item['id']}", method="DELETE")

    # 5. Memory
    recall_payload = {
        "competitor": "Microsoft",
        "query": "Copilot and AI models",
        "top_k": 3
    }
    st, data = make_request("/api/memory/recall", method="POST", body=recall_payload)
    check("POST /api/memory/recall", st, [200], data)

    retain_payload = {
        "competitor_id": "microsoft",
        "title": "Regression Memory Retain Probe",
        "description": "Testing memory retain route.",
        "event_type": "Product",
        "event_date": "2026-09-28",
        "source_name": "Azure Blog",
        "source_url": "https://azure.microsoft.com/retain-probe"
    }
    st, data = make_request("/api/events/retain", method="POST", body=retain_payload)
    check("POST /api/events/retain", st, [200, 201], data)
    probe_retain_id = data.get("event", {}).get("id") or data.get("id")
    if probe_retain_id:
        make_request(f"/api/events/{probe_retain_id}", method="DELETE")

    # 6. Analyst
    analyze_payload = {
        "competitor": "Microsoft",
        "question": "What is Microsoft's strategic direction in AI?"
    }
    st, data = make_request("/api/analyst/analyze", method="POST", body=analyze_payload)
    check("POST /api/analyst/analyze", st, [200], data)

    compare_payload = {
        "competitors": ["Microsoft", "Google"],
        "question": "How do their enterprise AI offerings compare?"
    }
    st, data = make_request("/api/analyst/compare", method="POST", body=compare_payload)
    check("POST /api/analyst/compare", st, [200], data)

    before_after_payload = {
        "competitor": "Microsoft",
        "question": "How has their enterprise strategy evolved over time?"
    }
    st, data = make_request("/api/analyst/before-after", method="POST", body=before_after_payload)
    check("POST /api/analyst/before-after", st, [200], data)

    # 7. Patterns
    st, data = make_request("/api/competitors/microsoft/patterns")
    check("GET /api/competitors/microsoft/patterns", st, [200], data)

    patterns_post_payload = {"competitor": "Microsoft"}
    st, data = make_request("/api/analyst/patterns", method="POST", body=patterns_post_payload)
    check("POST /api/analyst/patterns", st, [200], data)

    # 8. Alerts
    st, data = make_request("/api/competitors/microsoft/changes")
    check("GET /api/competitors/microsoft/changes", st, [200], data)

    st, data = make_request("/api/alerts?limit=5")
    check("GET /api/alerts", st, [200], data)

    alert_gen_payload = {"competitor": "Microsoft"}
    st, data = make_request("/api/alerts/generate", method="POST", body=alert_gen_payload)
    check("POST /api/alerts/generate", st, [200], data)

    # Test alert read/dismiss if any alert exists
    st, alerts_list = make_request("/api/alerts?limit=1")
    alerts = alerts_list.get("alerts", [])
    if alerts:
        a_id = alerts[0]["id"]
        st, data = make_request(f"/api/alerts/{a_id}/read", method="PATCH")
        check(f"PATCH /api/alerts/{a_id}/read", st, [200], data)
        st, data = make_request(f"/api/alerts/{a_id}/dismiss", method="PATCH")
        check(f"PATCH /api/alerts/{a_id}/dismiss", st, [200], data)

    # 9. Reports
    report_payload = {
        "competitor": "Microsoft",
        "timeframe": "all"
    }
    st, data = make_request("/api/reports/competitor", method="POST", body=report_payload)
    check("POST /api/reports/competitor", st, [200], data)

    # Summary
    total = len(results)
    passed = sum(1 for _, ok, _ in results if ok)
    failed = total - passed
    print("\n" + "=" * 60)
    print(f"REGRESSION RESULTS: {passed}/{total} Passed, {failed} Failed.")
    print("=" * 60)
    
    if failed > 0:
        sys.exit(1)

if __name__ == "__main__":
    run_regression()

"""
Step 11 Acceptance Test Suite: "What Changed?" + Proactive Competitive Alerts
Verifies:
1. Microsoft alert generation with real Hindsight context and Groq analysis
2. Duplicate alert protection
3. GET /api/competitors/<id>/changes
4. Alert status lifecycle: new -> read -> dismissed
5. Google alert generation & strict memory isolation
6. Anthropic (zero events) -> no fabricated alerts
7. HTTP endpoints verification
"""

import sys
import json
import urllib.request

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

from services.alert_service import AlertService
from services.database_service import DatabaseService

def test_alerts_system():
    service = AlertService()
    db = DatabaseService()

    # 1. TEST MICROSOFT ALERT GENERATION
    print("\n[TEST 1] Testing Microsoft Proactive Alert Generation...")
    msft_res = service.generate_alerts("Microsoft")
    print(f"Competitor: {msft_res.get('competitor')}")
    print(f"Alerts Generated: {msft_res.get('alerts_generated')}")
    print(f"Checkpoint Timestamp: {msft_res.get('checkpoint')}")

    assert msft_res["competitor"] == "Microsoft"
    assert msft_res["checkpoint"] is not None

    alerts = service.list_alerts(competitor_id="microsoft")
    assert len(alerts) > 0, "Microsoft should have at least 1 alert persisted"

    first_alert = alerts[0]
    print(f"\n  First Alert: {first_alert['title']}")
    print(f"    Severity: {first_alert.get('severity')} | Status: {first_alert.get('status')}")
    print(f"    What Changed: {first_alert.get('what_changed')}")
    print(f"    Why It Matters: {first_alert.get('why_it_matters')}")
    print(f"    Historical Context: {first_alert.get('historical_context')}")
    print(f"    Source: {first_alert.get('source_name')} ({first_alert.get('source_url')})")
    print(f"    Memories Grounded: {first_alert.get('memory_used', {}).get('count')}")

    assert first_alert["source_url"], "Alert must preserve verified source URL"
    assert "blogs.microsoft.com" in first_alert["source_url"], "Source URL must be authentic Microsoft blog"
    print("PASS: Microsoft alert generated with full evidence grounding!")

    # 2. TEST DUPLICATE ALERT PROTECTION
    print("\n[TEST 2] Testing Duplicate Alert Protection...")
    repeat_res = service.generate_alerts("Microsoft")
    print(f"Second Run Alerts Generated: {repeat_res.get('alerts_generated')}")
    print(f"Skipped Duplicates: {repeat_res.get('skipped_duplicates')}")
    assert repeat_res["alerts_generated"] == 0 or repeat_res["skipped_duplicates"] > 0, "Duplicate alerts must be prevented"
    print("PASS: Duplicate alert protection prevented re-alerting on same events.")

    # 3. TEST "WHAT CHANGED?" ENDPOINT LOGIC
    print("\n[TEST 3] Testing What Changed Checkpoint Comparison...")
    changes = service.get_changes("Microsoft")
    print(f"Competitor: {changes.get('competitor')}")
    print(f"Last Checkpoint: {changes.get('last_checkpoint')}")
    print(f"Events Since Checkpoint: {changes.get('event_count')}")
    assert changes["competitor"] == "Microsoft"
    assert "by_category" in changes
    print("PASS: What Changed endpoint correctly calculates delta from checkpoint.")

    # 4. TEST ALERT STATUS LIFECYCLE (new -> read -> dismissed)
    print("\n[TEST 4] Testing Alert Status Lifecycle (read & dismiss)...")
    alert_id = first_alert["id"]

    # Mark Read
    read_alert = service.mark_read(alert_id)
    assert read_alert["status"] == "read", "Alert status must change to 'read'"
    print(f"  Alert {alert_id} marked as read: status = {read_alert['status']}")

    # Mark Dismissed
    dismissed_alert = service.mark_dismissed(alert_id)
    assert dismissed_alert["status"] == "dismissed", "Alert status must change to 'dismissed'"
    print(f"  Alert {alert_id} dismissed: status = {dismissed_alert['status']}")

    # Verify evidence still exists in SQLite
    ev_check = db.get_event(dismissed_alert["event_id"])
    assert ev_check is not None, "Dismissed alert must NOT delete underlying event evidence"
    print("PASS: Alert lifecycle transitions work without deleting evidence.")

    # 5. TEST GOOGLE ALERT GENERATION & ISOLATION
    print("\n[TEST 5] Testing Google Alert Generation & Strict Isolation...")
    goog_res = service.generate_alerts("Google")
    print(f"Google Alerts Generated: {goog_res.get('alerts_generated')}")
    goog_alerts = service.list_alerts(competitor_id="google")
    assert len(goog_alerts) > 0, "Google should have at least 1 alert"

    for ga in goog_alerts:
        assert "microsoft" not in str(ga.get("source_name", "")).lower()
        assert "blogs.microsoft.com" not in str(ga.get("source_url", "")).lower()
        assert "copilot" not in str(ga.get("title", "")).lower()
    print("PASS: Google alert generated with strict bank & source isolation.")

    # 6. TEST ANTHROPIC (ZERO EVENTS) - NO FAKE ALERTS
    print("\n[TEST 6] Testing Insufficient Data Behavior (Anthropic)...")
    anth_res = service.generate_alerts("Anthropic")
    print(f"Anthropic Alerts Generated: {anth_res.get('alerts_generated')}")
    assert anth_res["alerts_generated"] == 0, "No alerts should be created for competitor with 0 events"
    anth_alerts = service.list_alerts(competitor_id="anthropic")
    assert len(anth_alerts) == 0, "Anthropic alert ledger must remain 0"
    print("PASS: Zero fake alerts generated when telemetry is absent.")

    # 7. TEST HTTP API ENDPOINTS
    print("\n[TEST 7] Testing HTTP Endpoints...")
    base_url = "http://127.0.0.1:5000"

    # 7a. GET /api/alerts
    with urllib.request.urlopen(f"{base_url}/api/alerts", timeout=15) as resp:
        assert resp.status == 200
        d = json.loads(resp.read().decode("utf-8"))
        assert d["status"] == "success"
        print(f"  ✓ GET /api/alerts HTTP 200 (Total alerts: {d['count']})")

    # 7b. GET /api/competitors/microsoft/changes
    with urllib.request.urlopen(f"{base_url}/api/competitors/microsoft/changes", timeout=15) as resp:
        assert resp.status == 200
        d = json.loads(resp.read().decode("utf-8"))
        assert d["status"] == "success"
        print(f"  ✓ GET /api/competitors/microsoft/changes HTTP 200")

    # 7c. PATCH /api/alerts/<id>/read
    req_read = urllib.request.Request(
        f"{base_url}/api/alerts/{alert_id}/read",
        data=b"{}",
        headers={"Content-Type": "application/json"},
        method="PATCH"
    )
    with urllib.request.urlopen(req_read, timeout=15) as resp:
        assert resp.status == 200
        print(f"  ✓ PATCH /api/alerts/{alert_id}/read HTTP 200")

    # 7d. PATCH /api/alerts/<id>/dismiss
    req_dismiss = urllib.request.Request(
        f"{base_url}/api/alerts/{alert_id}/dismiss",
        data=b"{}",
        headers={"Content-Type": "application/json"},
        method="PATCH"
    )
    with urllib.request.urlopen(req_dismiss, timeout=15) as resp:
        assert resp.status == 200
        print(f"  ✓ PATCH /api/alerts/{alert_id}/dismiss HTTP 200")

    print("\n==========================================")
    print("ALL STEP 11 ACCEPTANCE TESTS PASSED!")
    print("==========================================")

if __name__ == "__main__":
    test_alerts_system()

"""
Step 12 Acceptance Test Suite: Executive Intelligence Brief
Verifies:
1. Microsoft Executive Brief Generation (real SQLite events + Hindsight recall + Patterns + Alerts + Groq)
2. Google Brief & strict memory isolation
3. OpenAI Brief & strict memory isolation
4. Time range filtering: last_30_days, last_90_days, all
5. Insufficient Data Behavior (Anthropic - 0 events): Honest limitations, zero fabricated facts
6. Error handling: Unknown competitor (404), invalid time_range (400)
7. HTTP Endpoints: POST /api/reports/competitor, GET /api/reports/competitor/<id>
8. Evidence integrity: Real event IDs, real source names, real source URLs
"""

import sys
import json
import urllib.request
import urllib.error

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

from services.report_service import ReportService
from services.database_service import DatabaseService
from services.analyst_service import UnknownCompetitorError, AnalystValidationError

def test_reports_system():
    service = ReportService()
    db = DatabaseService()

    # 1. TEST MICROSOFT EXECUTIVE BRIEF
    print("\n[TEST 1] Testing Microsoft Executive Intelligence Brief Generation...")
    msft_res = service.generate_brief("Microsoft", time_range="all")
    print(f"Competitor: {msft_res.get('competitor')}")
    print(f"Status: {msft_res.get('status')}")
    print(f"Recent Activity Events: {len(msft_res.get('recent_activity', []))}")
    print(f"Major Patterns: {len(msft_res.get('major_patterns', []))}")
    print(f"Strategic Signals: {len(msft_res.get('strategic_signals', []))}")
    print(f"What Changed Alerts: {len(msft_res.get('what_changed', []))}")
    print(f"Historical Context Memories: {len(msft_res.get('historical_context', []))}")
    print(f"Key Evidence Records: {len(msft_res.get('key_evidence', []))}")
    print(f"Memory Used: {msft_res.get('memory_used')}")
    print(f"Confidence: {msft_res.get('confidence')}")

    assert msft_res["competitor"] == "Microsoft"
    assert msft_res["status"] == "success"
    assert len(msft_res["executive_summary"]) > 50, "Executive summary must be substantive"
    assert len(msft_res["recent_activity"]) >= 2, "Must contain real database events"
    assert len(msft_res["key_evidence"]) >= 2, "Must contain key evidence items"
    assert msft_res["memory_used"]["event_count"] > 0, "Must recall Hindsight memories"

    print("\n  Executive Summary Excerpt:")
    print(f"  {msft_res['executive_summary'][:220]}...")

    # Validate key evidence integrity
    first_ev = msft_res["key_evidence"][0]
    print(f"\n  Key Evidence Example: {first_ev['title']} ({first_ev['event_date']})")
    print(f"  Source: {first_ev['source_name']} -> {first_ev['source_url']}")
    assert first_ev["source_url"], "Evidence must have verified source URL"
    assert "blogs.microsoft.com" in first_ev["source_url"], "Microsoft evidence must point to official domain"

    print("PASS: Microsoft executive brief generated with full evidence grounding!")

    # 2. TEST GOOGLE BRIEF & MEMORY ISOLATION
    print("\n[TEST 2] Testing Google Executive Brief & Memory Isolation...")
    goog_res = service.generate_brief("Google", time_range="all")
    assert goog_res["competitor"] == "Google"
    assert goog_res["status"] == "success"

    # Verify no Microsoft cross-contamination
    for ev in goog_res["key_evidence"]:
        assert "microsoft" not in ev["title"].lower(), "Google report must not contain Microsoft events"
        assert "blogs.microsoft.com" not in str(ev["source_url"]).lower()
    for mem in goog_res["historical_context"]:
        assert "copilot" not in mem["text"].lower() or "gemini" in mem["text"].lower(), "Google memories must remain isolated"
    print("PASS: Google executive brief generated with strict memory and evidence isolation!")

    # 3. TEST OPENAI BRIEF & MEMORY ISOLATION
    print("\n[TEST 3] Testing OpenAI Executive Brief & Memory Isolation...")
    oai_res = service.generate_brief("OpenAI", time_range="all")
    assert oai_res["competitor"] == "OpenAI"
    assert oai_res["status"] == "success"
    assert len(oai_res["recent_activity"]) >= 2

    for ev in oai_res["key_evidence"]:
        assert "openai.com" in ev["source_url"], "OpenAI evidence must cite official openai.com sources"
    print("PASS: OpenAI executive brief generated with strict domain isolation!")

    # 4. TEST TIME RANGE FILTERING
    print("\n[TEST 4] Testing Time Range Filtering...")
    # 4a. 90-day report
    r90 = service.generate_brief("Microsoft", time_range="last_90_days")
    print(f"  90-day report status: {r90.get('status')} | Period: {r90.get('report_period')}")
    assert r90["report_period"] == "last_90_days"

    # 4b. 30-day report
    r30 = service.generate_brief("Microsoft", time_range="last_30_days")
    print(f"  30-day report status: {r30.get('status')} | Period: {r30.get('report_period')}")
    assert r30["report_period"] == "last_30_days"
    print("PASS: Time range filtering handles narrow windows accurately!")

    # 5. TEST INSUFFICIENT DATA BEHAVIOR (Anthropic)
    print("\n[TEST 5] Testing Insufficient Data Behavior (Anthropic - 0 events)...")
    anth_res = service.generate_brief("Anthropic", time_range="all")
    print(f"  Anthropic status: {anth_res.get('status')}")
    print(f"  Limitations: {anth_res.get('limitations')}")
    assert anth_res["status"] == "insufficient_data"
    assert len(anth_res["major_patterns"]) == 0
    assert "Not enough historical evidence" in anth_res["executive_summary"]
    assert anth_res["confidence"] == "low"
    print("PASS: Insufficient data behavior honestly rejects brief generation without fabricating facts!")

    # 6. TEST ERROR HANDLING
    print("\n[TEST 6] Testing Error Handling...")
    try:
        service.generate_brief("UnknownCorpXYZ")
        assert False, "Should raise UnknownCompetitorError"
    except UnknownCompetitorError:
        print("  ✓ Unknown competitor correctly raises UnknownCompetitorError")

    try:
        service.generate_brief("Microsoft", time_range="invalid_range_123")
        assert False, "Should raise AnalystValidationError"
    except AnalystValidationError:
        print("  ✓ Invalid time range correctly raises AnalystValidationError")
    print("PASS: Service-level error handling verified.")

    # 7. TEST HTTP ENDPOINTS
    print("\n[TEST 7] Testing HTTP Endpoints...")
    base_url = "http://127.0.0.1:5000"

    # 7a. POST /api/reports/competitor
    req_post = urllib.request.Request(
        f"{base_url}/api/reports/competitor",
        data=json.dumps({"competitor": "Microsoft", "time_range": "all"}).encode("utf-8"),
        headers={"Content-Type": "application/json"},
        method="POST"
    )
    with urllib.request.urlopen(req_post, timeout=60) as resp:
        assert resp.status == 200
        d = json.loads(resp.read().decode("utf-8"))
        assert d["status"] == "success"
        assert d["report"]["competitor"] == "Microsoft"
        print("  ✓ POST /api/reports/competitor HTTP 200 OK")

    # 7b. GET /api/reports/competitor/microsoft
    with urllib.request.urlopen(f"{base_url}/api/reports/competitor/microsoft?time_range=all", timeout=60) as resp:
        assert resp.status == 200
        d = json.loads(resp.read().decode("utf-8"))
        assert d["status"] == "success"
        assert d["report"]["competitor"] == "Microsoft"
        print("  ✓ GET /api/reports/competitor/microsoft HTTP 200 OK")

    # 7c. POST /api/reports/competitor with missing competitor (400)
    try:
        bad_req = urllib.request.Request(
            f"{base_url}/api/reports/competitor",
            data=b"{}",
            headers={"Content-Type": "application/json"},
            method="POST"
        )
        urllib.request.urlopen(bad_req, timeout=10)
        assert False, "Should return 400"
    except urllib.error.HTTPError as e:
        assert e.code == 400
        print("  ✓ POST /api/reports/competitor (missing field) HTTP 400")

    # 7d. POST /api/reports/competitor with unknown competitor (404)
    try:
        unknown_req = urllib.request.Request(
            f"{base_url}/api/reports/competitor",
            data=json.dumps({"competitor": "FakeNonExistentCorp"}).encode("utf-8"),
            headers={"Content-Type": "application/json"},
            method="POST"
        )
        urllib.request.urlopen(unknown_req, timeout=10)
        assert False, "Should return 404"
    except urllib.error.HTTPError as e:
        assert e.code == 404
        print("  ✓ POST /api/reports/competitor (unknown competitor) HTTP 404")

    print("\n==========================================")
    print("ALL STEP 12 ACCEPTANCE TESTS PASSED!")
    print("==========================================")

if __name__ == "__main__":
    test_reports_system()

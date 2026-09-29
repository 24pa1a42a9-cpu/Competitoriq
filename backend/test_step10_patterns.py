"""
Step 10 Strategic Pattern Detection & Connect the Dots Acceptance Tests
Verifies:
1. Microsoft Pattern Detection (Real events, Hindsight recall, Cross-category, Evidence verification)
2. Google Pattern Detection & Isolation
3. OpenAI Pattern Detection & Isolation
4. Insufficient Data Behavior (< 2 events, Anthropic)
5. Evidence Integrity (Real event IDs, real source names, real source URLs)
6. HTTP Endpoints:
   - POST /api/analyst/patterns
   - GET /api/competitors/<id>/patterns
"""

import sys
import json
import urllib.request

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

from services.pattern_service import PatternService
from services.database_service import DatabaseService

def test_pattern_service():
    service = PatternService()
    db = DatabaseService()

    # 1. TEST MICROSOFT PATTERNS
    print("\n[TEST 1] Testing Microsoft Strategic Pattern Detection...")
    msft_res = service.get_patterns("Microsoft")
    print(f"Competitor: {msft_res.get('competitor')}")
    print(f"Hindsight Memories Recalled: {msft_res['memory_used']['count']} ({msft_res['memory_used']['earliest']} to {msft_res['memory_used']['latest']})")
    print(f"Patterns Found: {len(msft_res.get('patterns', []))}")

    assert msft_res["competitor"] == "Microsoft"
    assert msft_res["memory_used"]["count"] > 0
    assert len(msft_res["patterns"]) > 0, "Microsoft should have at least 1 strategic pattern detected"

    for idx, p in enumerate(msft_res["patterns"], 1):
        print(f"\n  Pattern #{idx}: {p['title']}")
        print(f"    Confidence: {p['confidence'].upper()} | Categories: {p['categories']}")
        print(f"    Time Span: {p['time_span']['start']} -> {p['time_span']['end']}")
        print(f"    Supporting Events: {p['event_count']}")
        print(f"    Connection: {p['connection']}")
        print(f"    Strategic Signal: {p['strategic_signal']}")
        print(f"    Why It Matters: {p['why_it_matters']}")

        # Validate minimum 2 real events
        assert p["event_count"] >= 2, "Every pattern must have at least 2 real events"
        assert len(p["evidence"]) >= 2, "Evidence array must contain at least 2 items"

        # Validate evidence matches real SQLite records
        for ev in p["evidence"]:
            db_ev = db.get_event(ev["event_id"])
            assert db_ev is not None, f"Event ID {ev['event_id']} must exist in SQLite database"
            assert ev["source_url"], f"Evidence {ev['title']} must have a verified source URL"
            assert "blogs.microsoft.com" in ev["source_url"], f"Microsoft evidence URL must be official: {ev['source_url']}"

    print("PASS: Microsoft patterns detected with full evidence grounding!")

    # 2. TEST GOOGLE PATTERNS & ISOLATION
    print("\n[TEST 2] Testing Google Pattern Detection & Isolation...")
    goog_res = service.get_patterns("Google")
    print(f"Competitor: {goog_res.get('competitor')}")
    print(f"Hindsight Memories Recalled: {goog_res['memory_used']['count']}")
    print(f"Patterns Found: {len(goog_res.get('patterns', []))}")

    assert goog_res["competitor"] == "Google"
    assert len(goog_res["patterns"]) > 0

    # Strict isolation check: No Microsoft events/sources in Google patterns
    for p in goog_res["patterns"]:
        for ev in p["evidence"]:
            assert "microsoft" not in ev["source_name"].lower(), "Google pattern contaminated with Microsoft source!"
            assert "blogs.microsoft.com" not in ev["source_url"], "Google pattern contaminated with Microsoft URL!"
            assert "copilot" not in ev["title"].lower(), "Google pattern contaminated with Microsoft Copilot!"
    print("PASS: Google pattern detection succeeds with strict isolation!")

    # 3. TEST OPENAI PATTERNS & ISOLATION
    print("\n[TEST 3] Testing OpenAI Pattern Detection & Isolation...")
    oai_res = service.get_patterns("OpenAI")
    print(f"Competitor: {oai_res.get('competitor')}")
    print(f"Hindsight Memories Recalled: {oai_res['memory_used']['count']}")
    print(f"Patterns Found: {len(oai_res.get('patterns', []))}")

    assert oai_res["competitor"] == "OpenAI"
    assert len(oai_res["patterns"]) > 0

    # Strict isolation check: No Google or Microsoft events in OpenAI
    for p in oai_res["patterns"]:
        for ev in p["evidence"]:
            assert "blog.google" not in ev["source_url"], "OpenAI pattern contaminated with Google URL!"
            assert "blogs.microsoft.com" not in ev["source_url"], "OpenAI pattern contaminated with Microsoft URL!"
    print("PASS: OpenAI pattern detection succeeds with strict isolation!")

    # 4. TEST INSUFFICIENT DATA (< 2 events, Anthropic)
    print("\n[TEST 4] Testing Insufficient Data Behavior on Anthropic (0 events)...")
    anth_res = service.get_patterns("Anthropic")
    print(f"Competitor: {anth_res.get('competitor')}")
    print(f"Patterns Found: {len(anth_res.get('patterns', []))}")
    print(f"Limitations: {anth_res.get('limitations')}")

    assert len(anth_res["patterns"]) == 0, "No fake pattern should be generated for competitor with < 2 events"
    assert len(anth_res["limitations"]) > 0
    assert "Insufficient historical evidence" in anth_res["limitations"][0]
    print("PASS: Insufficient data behavior correctly returns empty patterns with honest explanation.")

    # 5. TEST HTTP ENDPOINTS
    print("\n[TEST 5] Testing HTTP Endpoints...")
    
    # 5a. POST /api/analyst/patterns
    payload = json.dumps({"competitor": "Microsoft"}).encode("utf-8")
    req = urllib.request.Request("http://127.0.0.1:5000/api/analyst/patterns", data=payload, headers={"Content-Type": "application/json"})
    with urllib.request.urlopen(req, timeout=60) as resp:
        assert resp.status == 200, f"Expected 200, got {resp.status}"
        data = json.loads(resp.read().decode("utf-8"))
        assert data["competitor"] == "Microsoft"
        assert len(data["patterns"]) > 0
        print("  ✓ POST /api/analyst/patterns HTTP 200 OK")

    # 5b. GET /api/competitors/microsoft/patterns
    req2 = urllib.request.Request("http://127.0.0.1:5000/api/competitors/microsoft/patterns")
    with urllib.request.urlopen(req2, timeout=60) as resp2:
        assert resp2.status == 200, f"Expected 200, got {resp2.status}"
        data2 = json.loads(resp2.read().decode("utf-8"))
        assert data2["status"] == "success"
        assert len(data2["patterns"]) > 0
        print("  ✓ GET /api/competitors/microsoft/patterns HTTP 200 OK")

    print("\n==========================================")
    print("ALL STEP 10 ACCEPTANCE TESTS PASSED!")
    print("==========================================")

if __name__ == "__main__":
    test_pattern_service()

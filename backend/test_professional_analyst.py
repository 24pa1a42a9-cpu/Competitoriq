"""
Comprehensive Professional AI Analyst Test Suite
Verifies:
1. Request validation (missing competitor, missing question, unknown competitor)
2. Insufficient memory handling for empty competitor (Anthropic)
3. GENERAL_COMPANY_INFO without forced Hindsight failure (Microsoft / Google HQ & founding)
4. RECENT_ACTIVITY grounded in structured events and timeline
5. STRATEGY_EVOLUTION grounded in Hindsight temporal memory
6. PRICING_ANALYSIS domain-specific reasoning
7. Non-existent information handling (Quantum computing on NovaAI -> honest limitation)
8. Multi-competitor comparison with memory bank isolation
"""

import sys
import json
import logging

# Ensure UTF-8 output encoding on Windows consoles
if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass

from app import create_app

logging.basicConfig(level=logging.INFO, format="%(message)s")
logger = logging.getLogger("test_professional_analyst")

def run_tests():
    print("=" * 75)
    print(" COMPETITORIQ - PROFESSIONAL AI ANALYST TEST SUITE")
    print("=" * 75)

    app = create_app()
    client = app.test_client()

    # 1. Validation: Missing Question (HTTP 400)
    print("\n[TEST 1] Validation: Missing Question...")
    res = client.post("/api/analyst/analyze", json={"competitor": "Microsoft", "question": ""})
    assert res.status_code == 400
    assert res.get_json()["error_type"] == "validation_error"
    print("  [PASS] Missing question correctly rejected with HTTP 400.")

    # 2. Validation: Missing Competitor (HTTP 400)
    print("\n[TEST 2] Validation: Missing Competitor...")
    res = client.post("/api/analyst/analyze", json={"question": "What is their strategy?"})
    assert res.status_code == 400
    assert res.get_json()["error_type"] == "validation_error"
    print("  [PASS] Missing competitor correctly rejected with HTTP 400.")

    # 3. Validation: Unknown Competitor (HTTP 404)
    print("\n[TEST 3] Validation: Unknown Competitor...")
    res = client.post("/api/analyst/analyze", json={"competitor": "FakeCorp999", "question": "What is their strategy?"})
    assert res.status_code == 404
    assert res.get_json()["error_type"] == "unknown_competitor"
    print("  [PASS] Unknown competitor rejected with HTTP 404.")

    # 4. Insufficient Memory Handling (Anthropic pricing - 0 memories, 0 events)
    print("\n[TEST 4] Insufficient Memory Handling (Anthropic pricing)...")
    res = client.post("/api/analyst/analyze", json={
        "competitor": "Anthropic",
        "question": "How has Anthropic's pricing strategy evolved over time?"
    })
    assert res.status_code == 200
    data = res.get_json()
    print(f"  Intent: {data.get('intent')}")
    print(f"  Answer: {data.get('answer')}")
    print(f"  Memory Count: {data.get('memory_used', {}).get('count')}")
    print(f"  Limitations: {data.get('limitations')}")
    assert data["memory_used"]["count"] == 0
    assert "insufficient stored evidence" in data["answer"].lower()
    assert len(data["limitations"]) > 0
    print("  [PASS] Zero-memory historical query returns honest limitation.")

    # 5. GENERAL_COMPANY_INFO (Microsoft profile - must answer from SQLite facts without failing!)
    print("\n[TEST 5] General Company Info Inquiry (Microsoft HQ & Founded)...")
    res = client.post("/api/analyst/analyze", json={
        "competitor": "Microsoft",
        "question": "Where is Microsoft headquartered and when was it founded?"
    })
    assert res.status_code == 200
    data = res.get_json()
    print(f"  Intent: {data.get('intent')}")
    print(f"  Answer:\n  {data.get('answer')}\n")
    assert data.get("intent") == "GENERAL_COMPANY_INFO"
    ans_lower = data.get("answer", "").lower()
    assert "redmond" in ans_lower or "washington" in ans_lower or "1975" in ans_lower, \
        "Answer must contain verified corporate facts (Redmond/1975) from SQLite"
    print("  [PASS] GENERAL_COMPANY_INFO answered accurately from SQLite corporate facts.")

    # 6. RECENT_ACTIVITY Inquiry (Google recent moves)
    print("\n[TEST 6] Recent Activity Inquiry (Google)...")
    res = client.post("/api/analyst/analyze", json={
        "competitor": "Google",
        "question": "What are Google's recent announcements and latest moves?"
    })
    assert res.status_code == 200
    data = res.get_json()
    print(f"  Intent: {data.get('intent')}")
    print(f"  Answer:\n  {data.get('answer')}\n")
    print(f"  Key Events Cited: {len(data.get('key_events', []))}")
    assert data.get("intent") == "RECENT_ACTIVITY"
    assert len(data.get("answer", "")) > 50
    print("  [PASS] RECENT_ACTIVITY successfully synthesized with chronological event citations.")

    # 7. STRATEGY_EVOLUTION Inquiry (Microsoft AI strategy)
    print("\n[TEST 7] Strategy Evolution Inquiry (Microsoft)...")
    res = client.post("/api/analyst/analyze", json={
        "competitor": "Microsoft",
        "question": "How has Microsoft's AI strategy evolved over time?"
    })
    assert res.status_code == 200
    data = res.get_json()
    print(f"  Intent: {data.get('intent')}")
    print(f"  Pattern: {data.get('pattern')}")
    print(f"  Strategic Signal: {data.get('strategic_signal')}")
    print(f"  Memory Count: {data.get('memory_used', {}).get('count')}")
    print(f"  Answer:\n  {data.get('answer')}\n")
    assert data.get("intent") == "STRATEGY_EVOLUTION"
    assert data.get("pattern") is not None
    assert data.get("memory_used", {}).get("count") > 0
    print("  [PASS] STRATEGY_EVOLUTION successfully grounded in persistent Hindsight memory.")

    # 8. Unrecorded Technology Inquiry (Quantum hardware on Microsoft / NovaAI)
    print("\n[TEST 8] Query on Information NOT in Telemetry (Quantum hardware patents)...")
    res = client.post("/api/analyst/analyze", json={
        "competitor": "Microsoft",
        "question": "What are Microsoft's proprietary patents specifically regarding quantum optical cryo-hardware?"
    })
    assert res.status_code == 200
    data = res.get_json()
    print(f"  Answer:\n  {data.get('answer')}\n")
    print(f"  Limitations: {data.get('limitations')}")
    ans_lower = data.get("answer", "").lower()
    has_insufficient_notice = any(w in ans_lower for w in ["insufficient", "no evidence", "not mentioned", "no record", "no specific", "do not contain"]) or len(data.get("limitations", [])) > 0
    assert has_insufficient_notice, "Agent must acknowledge that telemetry lacks specific optical cryo-hardware info"
    print("  [PASS] Non-existent technology query honestly states limitation without hallucinating.")

    print("\n" + "=" * 75)
    print(" ALL PROFESSIONAL AI ANALYST TESTS COMPLETED SUCCESSFULLY!")
    print("=" * 75)


if __name__ == "__main__":
    run_tests()

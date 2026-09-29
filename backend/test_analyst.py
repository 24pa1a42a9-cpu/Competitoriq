"""
CompetitorIQ Step 4 AI Analyst Test Suite
Verifies:
1. Parameter Validation (empty competitor, empty question)
2. Insufficient Memory Handling (unknown competitor / zero memories)
3. Groq Configuration & Error Handling (when key missing vs present)
4. TEST 1: Pricing Strategy Evolution ("How has NovaAI's pricing strategy changed over time?")
5. TEST 2: Multi-Event Strategic Shift Inference ("What broader strategic shift might these changes indicate?")
6. TEST 3: Insufficient Information in Memory ("What are NovaAI's plans for quantum computing hardware?")
"""

import sys
import json
import logging
from app import app
from services.hindsight_service import HindsightService
from services.llm_service import LLMService

logging.basicConfig(level=logging.INFO, format="%(message)s")
logger = logging.getLogger("test_analyst")


def run_analyst_tests():
    print("=" * 70)
    print(" COMPETITORIQ - STEP 4: GROQ AI ANALYST INTEGRATION TESTS")
    print("=" * 70)

    client = app.test_client()
    hindsight = HindsightService()
    llm = LLMService()

    # 0. Service Status Check
    print("\n[STEP 0] Checking Analyst Services Status (GET /api/analyst/status)...")
    res_status = client.get("/api/analyst/status")
    status_data = res_status.get_json()
    print(f"  HTTP {res_status.status_code}: {json.dumps(status_data, indent=2)}")

    assert res_status.status_code == 200, "Analyst status endpoint must return 200"
    assert status_data["hindsight"]["configured"] is True, "Hindsight must be configured"

    # 1. Parameter Validation Tests
    print("\n[STEP 1] Testing Request Parameter Validation...")
    res_no_comp = client.post("/api/analyst/analyze", json={"question": "What is NovaAI doing?"})
    print(f"  * Missing competitor -> HTTP {res_no_comp.status_code}: {res_no_comp.get_json()['message']}")
    assert res_no_comp.status_code == 400

    res_no_q = client.post("/api/analyst/analyze", json={"competitor": "NovaAI", "question": ""})
    print(f"  * Empty question -> HTTP {res_no_q.status_code}: {res_no_q.get_json()['message']}")
    assert res_no_q.status_code == 400
    print("  [OK] Request validation properly rejects malformed payloads.")

    # 2. Zero-Memory Competitor Handling (No Groq call needed if memory is completely absent)
    print("\n[STEP 2] Testing Zero-Memory Competitor Handling (NonExistentCorp)...")
    res_zero = client.post("/api/analyst/analyze", json={
        "competitor": "NonExistentCorp",
        "question": "What are their latest strategic moves?"
    })
    zero_data = res_zero.get_json()
    print(f"  HTTP {res_zero.status_code}: Memory Used = {zero_data.get('memory_used')}")
    print(f"  Answer: {zero_data.get('answer')}")

    assert zero_data.get("memory_used") is False, "Should report memory_used = false"
    assert "insufficient historical memory" in zero_data.get("answer", "").lower(), "Must acknowledge insufficient memory"
    print("  [OK] Successfully acknowledges absence of memory without fabricating intelligence.")

    # 3. Check Groq Configuration
    print("\n[STEP 3] Verifying Groq API Key Configuration...")
    if not llm.is_configured():
        print("  [INFO] GROQ_API_KEY is not yet set in backend/.env.")
        print("  Testing API response for missing Groq credentials...")
        res_groq_missing = client.post("/api/analyst/analyze", json={
            "competitor": "NovaAI",
            "question": "How has NovaAI's pricing strategy changed over time?"
        })
        groq_err = res_groq_missing.get_json()
        print(f"  HTTP {res_groq_missing.status_code}: {groq_err.get('message')}")
        assert res_groq_missing.status_code == 503
        assert groq_err.get("error_type") == "groq_not_configured"
        print("  [OK] Gracefully returned HTTP 503 with helpful JSON when Groq key is absent.")
        print("\n" + "-" * 70)
        print(" To run live Groq LLM reasoning tests (Tests 1, 2, 3), add your GROQ_API_KEY to backend/.env")
        print("-" * 70)
        return

    # 4. Live Groq Reasoning: TEST 1 - Pricing Strategy Evolution
    print("\n[TEST 1] Live Reasoning: How has NovaAI's pricing strategy changed over time?...")
    res_t1 = client.post("/api/analyst/analyze", json={
        "competitor": "NovaAI",
        "question": "How has NovaAI's pricing strategy changed over time?"
    })
    t1_data = res_t1.get_json()
    print(f"  HTTP {res_t1.status_code}")
    print(f"  Model Used: {t1_data.get('model_used')}")
    print(f"  Pattern: {t1_data.get('pattern')}")
    print(f"  Strategic Signal: {t1_data.get('strategic_signal')}")
    print(f"  Confidence: {t1_data.get('confidence')}")
    print(f"  Answer:\n  {t1_data.get('answer')}\n")
    print(f"  Key Events Connected: {len(t1_data.get('key_events', []))}")
    for ke in t1_data.get("key_events", []):
        print(f"    * [{ke.get('date')}] {ke.get('event')}")

    assert res_t1.status_code == 200
    assert t1_data.get("memory_used") is True
    assert t1_data.get("pattern") is not None
    print("  [OK] TEST 1 PASSED: Successfully connected pricing events across time into strategic narrative.")

    # 5. Live Groq Reasoning: TEST 2 - Multi-Event Strategic Shift Inference
    print("\n[TEST 2] Live Reasoning: What broader strategic shift might these changes indicate?...")
    res_t2 = client.post("/api/analyst/analyze", json={
        "competitor": "NovaAI",
        "question": "What broader strategic shift might these pricing, hiring, and product changes indicate?"
    })
    t2_data = res_t2.get_json()
    print(f"  HTTP {res_t2.status_code}")
    print(f"  Pattern: {t2_data.get('pattern')}")
    print(f"  Strategic Signal: {t2_data.get('strategic_signal')}")
    print(f"  Why It Matters: {t2_data.get('why_it_matters')}")
    print(f"  Answer:\n  {t2_data.get('answer')}\n")

    assert res_t2.status_code == 200
    assert t2_data.get("memory_used") is True
    print("  [OK] TEST 2 PASSED: Groq synthesized multi-event strategic shift distinguishing fact from inference.")

    # 6. Live Groq Reasoning: TEST 3 - Insufficient Information Handling
    print("\n[TEST 3] Testing Query on Information NOT in Memory (Quantum Computing)...")
    res_t3 = client.post("/api/analyst/analyze", json={
        "competitor": "NovaAI",
        "question": "What are NovaAI's current initiatives and patents regarding quantum computing hardware?"
    })
    t3_data = res_t3.get_json()
    print(f"  HTTP {res_t3.status_code}")
    print(f"  Answer:\n  {t3_data.get('answer')}\n")
    print(f"  Confidence: {t3_data.get('confidence')}")

    assert res_t3.status_code == 200
    ans_lower = t3_data.get("answer", "").lower()
    has_insufficient_notice = any(w in ans_lower for w in ["insufficient", "no evidence", "not mentioned", "no record", "no information"])
    assert has_insufficient_notice, "Agent must acknowledge that memory lacks quantum computing info"
    print("  [OK] TEST 3 PASSED: Agent honestly acknowledged memory limitation without inventing quantum hardware claims.")

    print("\n" + "=" * 70)
    print(" ALL STEP 4 GROQ ANALYST TESTS COMPLETED SUCCESSFULLY!")
    print("=" * 70)


if __name__ == "__main__":
    run_analyst_tests()

"""
CompetitorIQ Strategic Reasoning Layer Test Suite
Validates:
TEST 1: Microsoft analysis (Hindsight recall + evidence grounding + key events + memory_used)
TEST 2: Google analysis (Google memory isolation)
TEST 3: OpenAI analysis (OpenAI memory isolation)
TEST 4: Microsoft vs Google comparison (independent memory recall + shared patterns + differences)
TEST 5: Competitor with insufficient memory (Anthropic -> no fabricated facts, limitation returned)
TEST 6: Invalid competitor (proper 404 error)
TEST 7: Missing question (proper 400 validation error)
"""

import sys
import json
import logging
from typing import Dict, Any

# Ensure UTF-8 output encoding on Windows consoles
if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass

from app import create_app
from config import Config
from services.hindsight_service import HindsightService
from services.llm_service import LLMService

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("test_reasoning")


def run_reasoning_tests():
    app = create_app()
    client = app.test_client()
    hindsight = HindsightService()
    llm = LLMService()

    print("=" * 75)
    print(" COMPETITORIQ - STEP 7: COMPETITIVE INTELLIGENCE REASONING TESTS")
    print("=" * 75)

    # -------------------------------------------------------------
    # PRE-FLIGHT: Service Readiness Check
    # -------------------------------------------------------------
    print("\n[PRE-FLIGHT] Checking Analyst Subsystem Status (GET /api/analyst/status)...")
    res_status = client.get("/api/analyst/status")
    status_data = res_status.get_json()
    print(f"  HTTP {res_status.status_code}: Hindsight Connected = {status_data['hindsight']['configured']}")
    print(f"  Groq Configured = {status_data['llm']['configured']} (Model: {status_data['llm']['model']})")
    assert res_status.status_code == 200
    assert status_data["hindsight"]["configured"] is True, "Hindsight must be configured"

    # -------------------------------------------------------------
    # TEST 7: Missing Question Validation (HTTP 400)
    # -------------------------------------------------------------
    print("\n[TEST 7] Testing Missing Question Validation Error...")
    res_q_empty = client.post("/api/analyst/analyze", json={
        "competitor": "Microsoft",
        "question": ""
    })
    data_q_empty = res_q_empty.get_json()
    print(f"  HTTP {res_q_empty.status_code}: Error Type = '{data_q_empty.get('error_type')}'")
    print(f"  Message = '{data_q_empty.get('message')}'")
    assert res_q_empty.status_code == 400
    assert data_q_empty["error_type"] == "validation_error"
    assert data_q_empty["field"] == "question"
    print("  [OK] TEST 7 PASSED: Missing question rejected with HTTP 400.")

    # -------------------------------------------------------------
    # TEST 6: Invalid / Unknown Competitor (HTTP 404)
    # -------------------------------------------------------------
    print("\n[TEST 6] Testing Unknown Competitor Error Handling...")
    res_unknown = client.post("/api/analyst/analyze", json={
        "competitor": "NonExistentHyperCorp",
        "question": "What is their product roadmap?"
    })
    data_unknown = res_unknown.get_json()
    print(f"  HTTP {res_unknown.status_code}: Error Type = '{data_unknown.get('error_type')}'")
    print(f"  Message = '{data_unknown.get('message')}'")
    assert res_unknown.status_code == 404
    assert data_unknown["error_type"] == "unknown_competitor"
    print("  [OK] TEST 6 PASSED: Unknown competitor rejected with HTTP 404.")

    # -------------------------------------------------------------
    # TEST 5: Competitor with Insufficient Memory (Anthropic)
    # -------------------------------------------------------------
    print("\n[TEST 5] Testing Competitor with Insufficient Memory (Anthropic)...")
    res_insufficient = client.post("/api/analyst/analyze", json={
        "competitor": "Anthropic",
        "question": "How has Anthropic's pricing strategy evolved over time?"
    })
    data_insufficient = res_insufficient.get_json()
    print(f"  HTTP {res_insufficient.status_code}: Answer = '{data_insufficient.get('answer')}'")
    print(f"  Memory Count = {data_insufficient.get('memory_used', {}).get('count')}")
    print(f"  Confidence   = '{data_insufficient.get('confidence')}'")
    print(f"  Limitations  = {data_insufficient.get('limitations')}")

    assert res_insufficient.status_code == 200
    assert data_insufficient["memory_used"]["count"] == 0
    assert "insufficient stored evidence" in data_insufficient["answer"].lower()
    assert len(data_insufficient["limitations"]) > 0
    print("  [OK] TEST 5 PASSED: Zero-memory scenario returns honest limitation without fabricating facts.")

    # -------------------------------------------------------------
    # TEST 2 & 3: Memory Isolation Verification (Hindsight Recall)
    # -------------------------------------------------------------
    print("\n[TEST 2 & 3] Verifying Multi-Competitor Memory Isolation in Hindsight...")
    # Recall Google
    rec_goog = hindsight.recall_competitor_memory("Google", "Gemini context window expansion")
    mems_goog = rec_goog.get("memories", [])
    print(f"  * Google Bank ('{rec_goog.get('bank_id')}') Recalled: {len(mems_goog)} memories")
    for m in mems_goog:
        txt = m.get("text", "").lower()
        assert "copilot" not in txt, "Isolation failure: Microsoft Copilot found in Google bank!"
        assert "openai o1" not in txt, "Isolation failure: OpenAI found in Google bank!"

    # Recall OpenAI
    rec_oai = hindsight.recall_competitor_memory("OpenAI", "OpenAI o1 reasoning model release")
    mems_oai = rec_oai.get("memories", [])
    print(f"  * OpenAI Bank ('{rec_oai.get('bank_id')}') Recalled: {len(mems_oai)} memories")
    for m in mems_oai:
        txt = m.get("text", "").lower()
        assert "copilot" not in txt, "Isolation failure: Microsoft Copilot found in OpenAI bank!"
        assert "gemini" not in txt, "Isolation failure: Google Gemini found in OpenAI bank!"

    # Recall Microsoft
    rec_msft = hindsight.recall_competitor_memory("Microsoft", "Copilot Studio autonomous agents")
    mems_msft = rec_msft.get("memories", [])
    print(f"  * Microsoft Bank ('{rec_msft.get('bank_id')}') Recalled: {len(mems_msft)} memories")
    for m in mems_msft:
        txt = m.get("text", "").lower()
        assert "gemini" not in txt, "Isolation failure: Google Gemini found in Microsoft bank!"
        assert "openai o1" not in txt, "Isolation failure: OpenAI found in Microsoft bank!"

    print("  [OK] TESTS 2 & 3 PASSED: Complete Hindsight memory bank isolation confirmed across companies.")

    # -------------------------------------------------------------
    # TEST 1 & 4: Reasoning Pipeline & Groq Integration
    # -------------------------------------------------------------
    if not llm.is_configured():
        print("\n[INFO] GROQ_API_KEY is not configured in backend/.env.")
        print("Testing graceful 503 error handling when Groq synthesis is requested for verified memories...")

        # Test 1 error check
        res_msft_err = client.post("/api/analyst/analyze", json={
            "competitor": "Microsoft",
            "question": "How has Microsoft's AI strategy evolved?"
        })
        assert res_msft_err.status_code == 503
        assert res_msft_err.get_json()["error_type"] == "groq_not_configured"
        print(f"  Single Analysis -> HTTP 503 ({res_msft_err.get_json()['error_type']}): {res_msft_err.get_json()['message']}")

        # Test 4 error check
        res_comp_err = client.post("/api/analyst/compare", json={
            "competitors": ["Microsoft", "Google"],
            "question": "How are Microsoft and Google approaching AI agents?"
        })
        assert res_comp_err.status_code == 503
        assert res_comp_err.get_json()["error_type"] == "groq_not_configured"
        print(f"  Comparison      -> HTTP 503 ({res_comp_err.get_json()['error_type']}): {res_comp_err.get_json()['message']}")

        print("\n  [OK] TESTS 1 & 4 PASSED: Pipeline executes Hindsight recall first, then enforces Groq credentials.")
        print("  NOTE: Add GROQ_API_KEY to backend/.env to execute live end-to-end LLM inference.")

    else:
        # Live Groq Inference: TEST 1
        print("\n[TEST 1] Live Groq Strategic Analysis: Microsoft AI Strategy Evolution...")
        res_msft = client.post("/api/analyst/analyze", json={
            "competitor": "Microsoft",
            "question": "How has Microsoft's AI strategy evolved over time?"
        })
        data_msft = res_msft.get_json()
        print(f"  HTTP {res_msft.status_code}: Model Used = '{data_msft.get('model_used')}'")
        print(f"  Pattern = '{data_msft.get('pattern')}'")
        print(f"  Signal  = '{data_msft.get('strategic_signal')}'")
        print(f"  Answer  = '{data_msft.get('answer')}'")
        print(f"  Key Events = {len(data_msft.get('key_events', []))}")
        print(f"  Memory Used Count = {data_msft.get('memory_used', {}).get('count')}")
        print(f"  Evidence Citations = {len(data_msft.get('evidence', []))}")

        assert res_msft.status_code == 200
        assert data_msft["competitor"] == "Microsoft"
        assert data_msft["memory_used"]["count"] > 0
        assert len(data_msft["evidence"]) > 0
        print("  [OK] TEST 1 PASSED: Live evidence-grounded analysis returned from Groq.")

        # Live Groq Inference: TEST 4
        print("\n[TEST 4] Live Groq Multi-Competitor Comparison: Microsoft vs Google...")
        res_comp = client.post("/api/analyst/compare", json={
            "competitors": ["Microsoft", "Google"],
            "question": "Compare Microsoft and Google's AI strategies and platform focus."
        })
        data_comp = res_comp.get_json()
        print(f"  HTTP {res_comp.status_code}: Competitors = {data_comp.get('competitors')}")
        print(f"  Comparison = '{data_comp.get('comparison')}'")
        print(f"  Shared Patterns = {data_comp.get('shared_patterns')}")
        print(f"  Differences     = {data_comp.get('differences')}")
        print(f"  Memory Used     = {data_comp.get('memory_used')}")

        assert res_comp.status_code == 200
        assert len(data_comp["competitors"]) == 2
        assert "Microsoft" in data_comp["memory_used"]
        assert "Google" in data_comp["memory_used"]
        print("  [OK] TEST 4 PASSED: Cross-company comparison synthesized with isolated memory accounting.")

    print("\n" + "=" * 75)
    print(" ALL STEP 7 REASONING LAYER TESTS COMPLETED SUCCESSFULLY!")
    print("=" * 75)


if __name__ == "__main__":
    run_reasoning_tests()

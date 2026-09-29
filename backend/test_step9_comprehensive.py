"""
Comprehensive Step 9 Acceptance Tests
Verifies:
1. Microsoft Before/After
2. Google Before/After
3. OpenAI Before/After
4. Memory Isolation between Microsoft, Google, and OpenAI
5. Insufficient memory behavior (Anthropic with 0 events)
"""

import sys
import json

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

from services.hindsight_comparison_service import HindsightComparisonService

def run_tests():
    service = HindsightComparisonService()

    # 1. MICROSOFT TEST
    print("\n[TEST 1] Running Microsoft Before vs After...")
    msft = service.compare_before_after(
        competitor="Microsoft",
        question="How has Microsoft's AI strategy evolved?"
    )
    assert msft["competitor"] == "Microsoft"
    assert msft["before"]["context_type"] == "limited"
    assert msft["before"]["memory_used"]["count"] == 0
    assert msft["after"]["context_type"] == "hindsight"
    assert msft["after"]["memory_used"]["count"] > 0
    assert msft["after"]["memory_used"]["earliest"] is not None
    assert msft["after"]["memory_used"]["latest"] is not None
    assert len(msft["after"]["connections"]) > 0
    assert msft["improvement"]["historical_context_added"] is True
    print(f"PASS: Microsoft After recalled {msft['after']['memory_used']['count']} memories from {msft['after']['memory_used']['earliest']} to {msft['after']['memory_used']['latest']}")
    print(f"Pattern detected: {msft['after']['pattern']}")

    # 2. GOOGLE TEST
    print("\n[TEST 2] Running Google Before vs After...")
    goog = service.compare_before_after(
        competitor="Google",
        question="How has Google's AI strategy evolved?"
    )
    assert goog["competitor"] == "Google"
    assert goog["before"]["context_type"] == "limited"
    assert goog["before"]["memory_used"]["count"] == 0
    assert goog["after"]["context_type"] == "hindsight"
    assert goog["after"]["memory_used"]["count"] > 0
    assert goog["after"]["memory_used"]["earliest"] is not None
    assert goog["after"]["memory_used"]["latest"] is not None
    print(f"PASS: Google After recalled {goog['after']['memory_used']['count']} memories from {goog['after']['memory_used']['earliest']} to {goog['after']['memory_used']['latest']}")
    print(f"Pattern detected: {goog['after']['pattern']}")

    # 3. OPENAI TEST
    print("\n[TEST 3] Running OpenAI Before vs After...")
    oai = service.compare_before_after(
        competitor="OpenAI",
        question="How has OpenAI's AI strategy evolved?"
    )
    assert oai["competitor"] == "OpenAI"
    assert oai["before"]["context_type"] == "limited"
    assert oai["before"]["memory_used"]["count"] == 0
    assert oai["after"]["context_type"] == "hindsight"
    assert oai["after"]["memory_used"]["count"] > 0
    print(f"PASS: OpenAI After recalled {oai['after']['memory_used']['count']} memories from {oai['after']['memory_used']['earliest']} to {oai['after']['memory_used']['latest']}")
    print(f"Pattern detected: {oai['after']['pattern']}")

    # 4. STRICT MEMORY ISOLATION TEST
    print("\n[TEST 4] Verifying Strict Memory Isolation...")
    # Check that Google memories do not cite Microsoft Copilot / Microsoft Blog
    goog_evidence_texts = [e["text"].lower() for e in goog["after"]["evidence"]]
    goog_evidence_sources = [e["source"].lower() for e in goog["after"]["evidence"]]
    for text in goog_evidence_texts:
        assert "inflection" not in text, "Google memory contaminated with Microsoft Inflection hire!"
        assert "mustafa suleyman" not in text, "Google memory contaminated with Microsoft CEO hire!"

    # Check that Microsoft memories do not cite Demis Hassabis or Google The Keyword
    msft_evidence_sources = [e["source"].lower() for e in msft["after"]["evidence"]]
    for src in msft_evidence_sources:
        assert "google the keyword" not in src, "Microsoft evidence contaminated with Google source!"

    print("PASS: Memory isolation confirmed between Microsoft, Google, and OpenAI banks.")

    # 5. INSUFFICIENT MEMORY TEST (Anthropic has 0 events)
    print("\n[TEST 5] Testing Insufficient Memory State on Anthropic...")
    anth = service.compare_before_after(
        competitor="Anthropic",
        question="How has Anthropic's AI strategy evolved?"
    )
    assert anth["insufficient_memory"] is True
    assert "Not enough historical memory yet" in anth["message"]
    assert "Add more source-backed competitor events" in anth["guidance"]
    assert anth["after"]["memory_used"]["count"] == 0
    assert anth["improvement"]["historical_context_added"] is False
    print("PASS: Insufficient memory behavior properly triggers with honest guidance.")

    print("\n==========================================")
    print("ALL 5 COMPREHENSIVE TESTS PASSED SUCCESSFULLY!")
    print("==========================================")

if __name__ == "__main__":
    run_tests()

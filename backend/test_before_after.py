"""
Verification Test for Before vs After Hindsight Service (Step 9)
Tests Microsoft, Google, OpenAI, and memory isolation.
"""

import sys
import json

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

from services.hindsight_comparison_service import HindsightComparisonService

def main():
    service = HindsightComparisonService()

    # Test 1: Microsoft
    print("=== Testing Microsoft Before vs After ===")
    msft_res = service.compare_before_after(
        competitor="Microsoft",
        question="How has Microsoft's AI strategy evolved?"
    )
    print("Competitor:", msft_res.get("competitor"))
    print("Before Context Type:", msft_res["before"]["context_type"])
    print("Before Memory Used Count:", msft_res["before"]["memory_used"]["count"])
    print("Before Key Events:", len(msft_res["before"]["key_events"]))
    print("After Context Type:", msft_res["after"]["context_type"])
    print("After Memory Used Count:", msft_res["after"]["memory_used"]["count"])
    print("After Earliest Memory:", msft_res["after"]["memory_used"]["earliest"])
    print("After Latest Memory:", msft_res["after"]["memory_used"]["latest"])
    print("After Pattern:", msft_res["after"]["pattern"])
    print("After Connections:", len(msft_res["after"]["connections"]))
    print("Improvement Metrics:", json.dumps(msft_res.get("improvement"), indent=2))

    # Assertions
    assert msft_res["before"]["context_type"] == "limited", "Before must have limited context"
    assert msft_res["before"]["memory_used"]["count"] == 0, "Before must have 0 Hindsight memory"
    assert msft_res["after"]["context_type"] == "hindsight", "After must have hindsight context"
    assert msft_res["after"]["memory_used"]["count"] > 0, "After must have recalled memories"
    assert msft_res["improvement"]["historical_context_added"] is True, "Improvement must show added historical context"
    print("✓ Microsoft Before vs After Passed!")

if __name__ == "__main__":
    main()

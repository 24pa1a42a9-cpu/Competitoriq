"""
Unit test suite for Question Intent Classification.
Verifies all 19 canonical intents and data source routing.
"""

from services.intent_service import QuestionIntentClassifier, ALL_INTENTS

def test_all_canonical_intents():
    classifier = QuestionIntentClassifier()

    test_queries = [
        ("Who is Microsoft and where are they headquartered?", "GENERAL_COMPANY_INFO"),
        ("What are the latest moves by Google?", "RECENT_ACTIVITY"),
        ("What has been OpenAI historical strategy?", "HISTORICAL_STRATEGY"),
        ("What AI products does Microsoft offer?", "PRODUCT_ANALYSIS"),
        ("How has NovaAI pricing strategy changed over time?", "PRICING_ANALYSIS"),
        ("Who is Anthropic hiring?", "HIRING_ANALYSIS"),
        ("What strategic partnerships has Microsoft formed?", "PARTNERSHIP_ANALYSIS"),
        ("What companies did Microsoft acquire?", "ACQUISITION_ANALYSIS"),
        ("What foundation model architecture does Google use?", "TECHNOLOGY_ANALYSIS"),
        ("How has OpenAI messaging and branding shifted?", "MESSAGING_ANALYSIS"),
        ("How has Microsoft AI strategy evolved?", "STRATEGY_EVOLUTION"),
        ("Compare Microsoft and Google in enterprise AI", "COMPETITOR_COMPARISON"),
        ("Why did they launch Copilot Studio?", "EVENT_EXPLANATION"),
        ("What patterns do you see in Google moves?", "PATTERN_ANALYSIS"),
        ("What has changed since last month for Microsoft?", "WHAT_CHANGED"),
        ("Give me an executive summary of OpenAI", "EXECUTIVE_SUMMARY"),
        ("What is stored in Hindsight memory for Google?", "MEMORY_QUERY"),
        ("What is Microsoft primary battleground and threat level?", "GENERAL_COMPETITIVE_INTELLIGENCE"),
        ("Random query regarding unrelated topic", "UNKNOWN")
    ]

    print(f"Total Canonical Intents Defined: {len(ALL_INTENTS)}")
    assert len(ALL_INTENTS) == 19, "Must have exactly 19 canonical intents"

    passed = 0
    for q, expected in test_queries:
        res = classifier.classify(q)
        match = (res.intent == expected)
        if match:
            passed += 1
            print(f"  [PASS] {expected:<35} <- '{q}' (needs_hindsight={res.needs_hindsight}, needs_sqlite={res.needs_sqlite_events})")
        else:
            print(f"  [FAIL] Expected {expected}, got {res.intent} <- '{q}'")

    print(f"\nClassification results: {passed}/{len(test_queries)} passed.")
    assert passed == len(test_queries), "All canonical intent classifications must pass."

    # Test company info does NOT force Hindsight
    comp_info_res = classifier.classify("Where is Microsoft headquartered and when was it founded?")
    assert comp_info_res.intent == "GENERAL_COMPANY_INFO"
    assert comp_info_res.needs_hindsight is False
    assert comp_info_res.needs_sqlite_profile is True
    print("  [PASS] GENERAL_COMPANY_INFO properly avoids forced Hindsight dependency.")

    # Test comparison detects multiple competitors
    comp_res = classifier.classify("Compare Microsoft and Google")
    assert comp_res.intent == "COMPETITOR_COMPARISON"
    assert "microsoft" in comp_res.detected_competitors
    assert "google" in comp_res.detected_competitors
    print("  [PASS] COMPETITOR_COMPARISON correctly detects both competitors.")

    print("\nALL INTENT CLASSIFICATION TESTS PASSED!")


if __name__ == "__main__":
    test_all_canonical_intents()

"""
CompetitorIQ Hindsight Step 3 Verification Test Suite
Tests:
1. GET  /api/test/hindsight/status    -> Verified connectivity with Hindsight Cloud
2. POST /api/test/hindsight/retain    -> Retain 5 chronological events for NovaAI
3. POST /api/test/hindsight/recall    -> Recall memories for NovaAI via natural-language query
4. POST /api/test/hindsight/isolation -> Verify memory isolation between NovaAI and CloudMind
"""

import sys
import json
import logging
from app import app
from services.hindsight_service import HindsightService

# Configure logging
logging.basicConfig(level=logging.INFO, format="%(message)s")
logger = logging.getLogger("test_hindsight")


def run_verification():
    print("=" * 70)
    print(" COMPETITORIQ - STEP 3: HINDSIGHT RETAIN + RECALL VERIFICATION")
    print("=" * 70)

    client = app.test_client()

    # 1. Diagnostic Status Test
    print("\n[STEP 1] Testing GET /api/test/hindsight/status ...")
    res_status = client.get("/api/test/hindsight/status")
    status_data = res_status.get_json()
    print(f"  HTTP Status: {res_status.status_code}")
    print(f"  Payload: {json.dumps(status_data, indent=2)}")

    assert res_status.status_code == 200, f"Expected 200, got {res_status.status_code}"
    assert status_data.get("configured") is True, "Hindsight must be configured"
    assert status_data.get("connected") is True, "Hindsight must be connected"
    assert status_data.get("memory_system") == "hindsight", "Memory system must be hindsight"
    print("  [OK] Hindsight connection verified operational!")

    # 2. RETAIN Test (5 Chronological Events for NovaAI)
    print("\n[STEP 2] Testing POST /api/test/hindsight/retain (5 chronological events)...")
    res_retain = client.post("/api/test/hindsight/retain")
    retain_data = res_retain.get_json()
    print(f"  HTTP Status: {res_retain.status_code}")
    print(f"  Success: {retain_data.get('success')}")
    print(f"  Operation: {retain_data.get('operation')}")
    print(f"  Memory System: {retain_data.get('memory_system')}")
    print(f"  Events Retained: {retain_data.get('events_retained')}")

    assert res_retain.status_code == 200, f"Expected 200, got {res_retain.status_code}"
    assert retain_data.get("success") is True, "Retain operation must succeed"
    assert retain_data.get("memory_system") == "hindsight", "Memory system must be hindsight"
    assert retain_data.get("operation") == "retain", "Operation must be retain"
    assert retain_data.get("events_retained") >= 5, "Must retain at least 5 events"

    for idx, item in enumerate(retain_data.get("details", []), 1):
        print(f"    {idx}. [{item['event_date']}] ({item['category']}) {item['title'][:60]}... -> Bank: {item['hindsight_bank']}")
    print("  [OK] RETAIN verified! 5 realistic historical events retained in Hindsight.")

    # 3. RECALL Test (Natural-Language Query)
    print("\n[STEP 3] Testing POST /api/test/hindsight/recall ...")
    query_payload = {
        "competitor": "NovaAI",
        "query": "How has NovaAI's pricing strategy changed over time?"
    }
    res_recall = client.post("/api/test/hindsight/recall", json=query_payload)
    recall_data = res_recall.get_json()
    print(f"  HTTP Status: {res_recall.status_code}")
    print(f"  Competitor: {recall_data.get('competitor')}")
    print(f"  Query: {recall_data.get('query')}")
    print(f"  Bank ID: {recall_data.get('bank_id')}")
    print(f"  Memory System: {recall_data.get('memory_system')}")
    print(f"  Recalled Memories Count: {recall_data.get('count')}")

    assert res_recall.status_code == 200, f"Expected 200, got {res_recall.status_code}"
    assert recall_data.get("success") is True, "Recall operation must succeed"
    assert recall_data.get("competitor") == "NovaAI", "Competitor must match"
    assert recall_data.get("memory_system") == "hindsight", "Memory system must be hindsight"
    assert recall_data.get("count") > 0, "Should recall at least one memory"

    memories = recall_data.get("recalled_memories", [])
    print("\n  Sample Recalled Historical Memories from Hindsight:")
    for idx, mem in enumerate(memories[:3], 1):
        score_info = mem.get("scores", {})
        final_score = score_info.get("final") if isinstance(score_info, dict) else None
        print(f"    {idx}. [Score: {final_score}] {mem.get('text')}")
        if mem.get("occurred_start"):
            print(f"       Indexed Date: {mem.get('occurred_start')}")

    print("  [OK] RECALL verified! Real memories retrieved from Hindsight.")

    # 4. Memory Isolation Test (NovaAI vs CloudMind)
    print("\n[STEP 4] Testing POST /api/test/hindsight/isolation ...")
    res_iso = client.post("/api/test/hindsight/isolation")
    iso_data = res_iso.get_json()
    print(f"  HTTP Status: {res_iso.status_code}")
    print(f"  Isolation Verified: {iso_data.get('isolation_verified')}")
    print(f"  NovaAI Bank: {iso_data.get('novaai_bank')}")
    print(f"  CloudMind Bank: {iso_data.get('cloudmind_bank')}")
    print(f"  CloudMind Leaked Into NovaAI: {iso_data.get('cloudmind_leaked_into_novaai')}")
    print(f"  NovaAI Memories Count: {iso_data.get('novaai_memories_count')}")
    print(f"  CloudMind Memories Count: {iso_data.get('cloudmind_memories_count')}")
    print(f"  Details: {iso_data.get('verification_details')}")

    assert res_iso.status_code == 200, f"Expected 200, got {res_iso.status_code}"
    assert iso_data.get("isolation_verified") is True, "Isolation must be verified"
    assert iso_data.get("cloudmind_leaked_into_novaai") is False, "No cross-contamination allowed"
    print("  [OK] MEMORY ISOLATION verified! NovaAI and CloudMind memories remain strictly separated.")

    print("\n" + "=" * 70)
    print(" ALL STEP 3 VERIFICATION TESTS PASSED SUCCESSFULLY WITH REAL HINDSIGHT!")
    print("=" * 70)


if __name__ == "__main__":
    run_verification()

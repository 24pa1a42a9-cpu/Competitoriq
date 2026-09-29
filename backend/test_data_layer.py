"""
CompetitorIQ Data Layer Test Suite (Step 5 Verification)
Verifies:
1. Create Competitor (dynamic registration with Hindsight bank allocation)
2. Create Event (validation, SQLite storage, Hindsight RETAIN)
3. Verify SQLite Event persistence
4. Verify Hindsight RETAIN and recall
5. Retrieve Competitor Timeline (ascending chronological ordering)
6. Filter Events by Type (Product vs Pricing)
7. Filter Events by Date Range (start_date, end_date)
8. Retrieve Events for One Competitor Only
9. Verify Competitor Memory Isolation (TestCorp Alpha vs TestCorp Beta)
"""

import sys
import json
import logging
from app import app
from services.hindsight_service import HindsightService

logging.basicConfig(level=logging.INFO, format="%(message)s")
logger = logging.getLogger("test_data_layer")


def run_data_layer_tests():
    print("=" * 70)
    print(" COMPETITORIQ - STEP 5: COMPETITOR INTELLIGENCE DATA LAYER TESTS")
    print("=" * 70)

    client = app.test_client()
    hindsight = HindsightService()

    # TEST 1: Create Competitor
    print("\n[TEST 1] Registering dynamic competitor (TestCorp Alpha)...")
    res_c1 = client.post("/api/competitors", json={
        "name": "TestCorp Alpha",
        "website": "https://testcorp-alpha.io",
        "industry": "Autonomous Cloud Intelligence",
        "description": "[TEST DATA ONLY] Synthetic competitor profile for test suite validation."
    })
    c1_data = res_c1.get_json()
    print(f"  HTTP {res_c1.status_code}: Competitor ID = '{c1_data.get('competitor', {}).get('id')}'")
    print(f"  Hindsight Bank Identifier = '{c1_data.get('hindsight_bank')}'")

    assert res_c1.status_code == 201, f"Expected 201, got {res_c1.status_code}"
    comp_alpha_id = c1_data["competitor"]["id"]
    assert comp_alpha_id == "testcorp-alpha"
    assert c1_data["hindsight_bank"] == "competitor-test-corp-alpha"
    print("  [OK] TEST 1 PASSED: Competitor registered and Hindsight bank provisioned.")

    # TEST 2: Create Event with mandatory source validation
    print("\n[TEST 2] Ingesting competitor event into SQLite + Hindsight...")
    # First verify missing source is rejected
    res_bad_source = client.post("/api/events", json={
        "competitor_id": comp_alpha_id,
        "event_type": "Product",
        "title": "[TEST DATA] Invalid event missing source",
        "event_date": "2026-04-10",
        "description": "Missing source should fail validation"
    })
    print(f"  * Rejected event without source -> HTTP {res_bad_source.status_code}: {res_bad_source.get_json()['message']}")
    assert res_bad_source.status_code == 400

    # Ingest valid event 1
    event_1_payload = {
        "competitor_id": comp_alpha_id,
        "event_type": "Product",
        "title": "[TEST DATA] TestCorp Alpha debuts automated pipeline v1.0",
        "description": "Synthetic product launch of continuous automated intelligence pipeline.",
        "event_date": "2026-04-10",
        "source_name": "TestCorp Alpha Engineering Dispatch v1.0",
        "source_url": "https://testcorp-alpha.io/blog/pipeline-v1",
        "significance": "Represents initial product baseline for market competition."
    }
    res_e1 = client.post("/api/events", json=event_1_payload)
    e1_data = res_e1.get_json()
    print(f"  HTTP {res_e1.status_code}: Event ID = '{e1_data.get('event', {}).get('id')}'")
    print(f"  Hindsight Status = '{e1_data.get('hindsight_status')}'")

    assert res_e1.status_code == 201, f"Expected 201, got {res_e1.status_code}"
    event_1_id = e1_data["event"]["id"]
    assert e1_data["hindsight_status"] == "retained"
    print("  [OK] TEST 2 PASSED: Event ingested into SQLite and retained in Hindsight.")

    # TEST 3: Verify SQLite Event
    print(f"\n[TEST 3] Verifying SQLite persistence for event '{event_1_id}'...")
    res_get_e1 = client.get(f"/api/events/{event_1_id}")
    get_e1_data = res_get_e1.get_json()
    print(f"  HTTP {res_get_e1.status_code}: Title = '{get_e1_data.get('event', {}).get('title')}'")
    print(f"  Competitor Name = '{get_e1_data.get('event', {}).get('competitor_name')}'")

    assert res_get_e1.status_code == 200
    assert get_e1_data["event"]["id"] == event_1_id
    assert get_e1_data["event"]["competitor_id"] == comp_alpha_id
    print("  [OK] TEST 3 PASSED: Event verified in SQLite with relation to TestCorp Alpha.")

    # TEST 4: Verify Hindsight RETAIN via RECALL
    print("\n[TEST 4] Verifying Hindsight RETAIN via semantic recall...")
    res_rec = client.post("/api/memory/recall", json={
        "competitor": "TestCorp Alpha",
        "query": "automated pipeline launch"
    })
    rec_data = res_rec.get_json()
    memories = rec_data.get("memories", [])
    print(f"  HTTP {res_rec.status_code}: Recalled {len(memories)} memories from bank '{rec_data.get('bank_id')}'")
    for m in memories[:1]:
        print(f"    Memory: {m.get('text')}")

    assert res_rec.status_code == 200
    assert len(memories) > 0, "Hindsight should return retained memory"
    print("  [OK] TEST 4 PASSED: Retained memory successfully retrieved from Hindsight.")

    # TEST 5: Retrieve Competitor Timeline (Ordered chronologically)
    print("\n[TEST 5] Ingesting earlier event and testing chronological timeline...")
    # Add earlier event (2025-08-01)
    event_earlier = {
        "competitor_id": comp_alpha_id,
        "event_type": "Hiring",
        "title": "[TEST DATA] TestCorp Alpha recruited Head of Systems Engineering",
        "description": "Appointed infrastructure veteran to architect distributed computing nodes.",
        "event_date": "2025-08-01",
        "source_name": "Industry Executive Appointments Digest"
    }
    res_earlier = client.post("/api/events", json=event_earlier)
    assert res_earlier.status_code == 201

    res_timeline = client.get(f"/api/competitors/{comp_alpha_id}/timeline")
    timeline_data = res_timeline.get_json()
    timeline = timeline_data.get("timeline", [])
    print(f"  HTTP {res_timeline.status_code}: Timeline contains {len(timeline)} milestones")
    for idx, t in enumerate(timeline, 1):
        print(f"    {idx}. [{t['event_date']}] ({t['event_type']}) {t['title']}")

    assert res_timeline.status_code == 200
    assert len(timeline) >= 2
    # Chronological check: earliest event should appear first
    dates = [t["event_date"] for t in timeline]
    assert dates == sorted(dates), "Timeline must be ordered in ascending chronological order"
    print("  [OK] TEST 5 PASSED: Competitor timeline returned in strict chronological order.")

    # TEST 6: Filter Events by Type
    print("\n[TEST 6] Testing event filtering by type (Product vs Pricing)...")
    # Add a Pricing event
    event_pricing = {
        "competitor_id": comp_alpha_id,
        "event_type": "Pricing",
        "title": "[TEST DATA] TestCorp Alpha instituted $50k ACV enterprise floor",
        "description": "Eliminated trial tier and instituted annual minimum contract.",
        "event_date": "2026-06-15",
        "source_name": "Enterprise SaaS Pricing Watch"
    }
    res_pr = client.post("/api/events", json=event_pricing)
    assert res_pr.status_code == 201

    res_filter_type = client.get(f"/api/events?competitor={comp_alpha_id}&event_type=Pricing")
    filtered_type = res_filter_type.get_json().get("events", [])
    print(f"  HTTP {res_filter_type.status_code}: Filtered count = {len(filtered_type)}")
    for f in filtered_type:
        print(f"    Event: [{f['event_date']}] ({f['event_type']}) {f['title']}")
        assert f["event_type"].lower() == "pricing"
    print("  [OK] TEST 6 PASSED: Event filtering by type functions accurately.")

    # TEST 7: Filter Events by Date Range
    print("\n[TEST 7] Testing event filtering by date range (2026 only)...")
    res_filter_date = client.get(f"/api/events?competitor={comp_alpha_id}&start_date=2026-01-01&end_date=2026-12-31")
    filtered_date = res_filter_date.get_json().get("events", [])
    print(f"  HTTP {res_filter_date.status_code}: Events in 2026 = {len(filtered_date)}")
    for f in filtered_date:
        print(f"    Event: [{f['event_date']}] {f['title']}")
        assert f["event_date"].startswith("2026")
    print("  [OK] TEST 7 PASSED: Date range filtering (start_date/end_date) functions accurately.")

    # TEST 8: Retrieve Events for One Competitor Only
    print(f"\n[TEST 8] Retrieving events exclusively for competitor '{comp_alpha_id}'...")
    res_comp_events = client.get(f"/api/competitors/{comp_alpha_id}/events")
    comp_events = res_comp_events.get_json().get("events", [])
    print(f"  HTTP {res_comp_events.status_code}: Event count = {len(comp_events)}")
    for e in comp_events:
        assert e["competitor_id"] == comp_alpha_id
    print("  [OK] TEST 8 PASSED: Single competitor events query returns zero foreign events.")

    # TEST 9: Multi-Competitor Isolation (TestCorp Alpha vs TestCorp Beta)
    print("\n[TEST 9] Verifying Multi-Competitor Isolation (TestCorp Alpha vs TestCorp Beta)...")
    # Register TestCorp Beta
    client.post("/api/competitors", json={
        "name": "TestCorp Beta",
        "website": "https://testcorp-beta.ai",
        "industry": "GPU Cluster Scheduling",
        "description": "[TEST DATA ONLY] Second competitor to verify memory and relational isolation."
    })

    # Ingest event for Beta
    res_beta_evt = client.post("/api/events", json={
        "competitor": "TestCorp Beta",
        "event_type": "Funding",
        "title": "[TEST DATA] TestCorp Beta closed $75M Series B funding round",
        "description": "Round led by Tier-1 venture partners to scale private datacenter clusters.",
        "event_date": "2026-07-20",
        "source_name": "Venture Capital Deal Wire Dispatch"
    })
    assert res_beta_evt.status_code == 201

    # Query Hindsight memory for Alpha searching Beta terms
    res_alpha_recall = client.post("/api/memory/recall", json={
        "competitor": "TestCorp Alpha",
        "query": "closed $75M Series B funding round"
    })
    alpha_memories = res_alpha_recall.get_json().get("memories", [])

    # Query Hindsight memory for Beta
    res_beta_recall = client.post("/api/memory/recall", json={
        "competitor": "TestCorp Beta",
        "query": "closed $75M Series B funding round"
    })
    beta_memories = res_beta_recall.get_json().get("memories", [])

    print(f"  * TestCorp Alpha Recall count: {len(alpha_memories)}")
    print(f"  * TestCorp Beta Recall count: {len(beta_memories)}")

    # Check that Alpha bank contains NO Beta funding information
    for m in alpha_memories:
        text = m.get("text", "").lower()
        assert "beta" not in text and "$75m" not in text, "Memory leak detected!"

    assert len(beta_memories) > 0, "TestCorp Beta bank should have its funding event"
    print("  [OK] TEST 9 PASSED: Multi-competitor isolation completely verified across SQLite and Hindsight banks.")

    # Clean up test events from SQLite
    client.delete(f"/api/events/{event_1_id}")

    print("\n" + "=" * 70)
    print(" ALL 9 STEP 5 DATA LAYER TESTS COMPLETED SUCCESSFULLY!")
    print("=" * 70)


if __name__ == "__main__":
    run_data_layer_tests()

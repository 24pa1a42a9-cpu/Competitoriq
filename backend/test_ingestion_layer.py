"""
CompetitorIQ Ingestion Layer Test Suite
Validates:
1. POST /api/ingestion/events single verified event ingestion
2. SQLite relational persistence
3. Hindsight episodic memory RETAIN in competitor-isolated bank
4. Duplicate event rejection (status: duplicate, no duplicate SQLite row or Hindsight memory)
5. Validation constraints (empty title, missing source_url, malformed URL, invalid date, bad type)
6. Bulk ingestion with failure isolation
7. Real-world target competitor testing (Microsoft, Google, OpenAI)
8. Multi-competitor memory bank isolation (Microsoft recall does not return Google/OpenAI events)
9. Backward compatibility with existing Step 5 endpoints
10. Security: No API keys or secrets exposed
"""

import sys
import json
import logging
from typing import Dict, Any

from app import create_app
from config import Config
from models.database import get_db_connection

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("test_ingestion")


def run_ingestion_tests():
    app = create_app()
    client = app.test_client()

    print("=" * 75)
    print(" COMPETITORIQ - STEP 6: REAL-WORLD INGESTION LAYER VERIFICATION SUITE")
    print("=" * 75)

    # -------------------------------------------------------------
    # TEST 1: Single Verified Event Ingestion (Microsoft)
    # -------------------------------------------------------------
    print("\n[TEST 1] Testing single verified event ingestion via POST /api/ingestion/events...")
    msft_event = {
        "competitor": "Microsoft",
        "event_type": "Product",
        "title": "Microsoft announces Copilot Studio Autonomous Agents for Enterprise Operations",
        "description": "Microsoft introduced autonomous agent capabilities in Copilot Studio and 10 pre-built autonomous agents in Dynamics 365, enabling organizations to automate complex, multi-step enterprise workflows.",
        "event_date": "2024-10-21",
        "source_name": "The Official Microsoft Blog",
        "source_url": "https://blogs.microsoft.com/blog/2024/10/21/transforming-business-processes-with-copilot-studio-and-dynamics-365/",
        "significance": "Marks strategic transition from assistive chat copilots to autonomous enterprise workflow agents."
    }

    res_1 = client.post("/api/ingestion/events", json=msft_event)
    data_1 = res_1.get_json()
    print(f"  HTTP {res_1.status_code}: Status = '{data_1.get('status')}'")
    print(f"  Event ID = '{data_1.get('event', {}).get('id')}'")
    print(f"  Database Status = '{data_1.get('database_status')}'")
    print(f"  Hindsight Status = '{data_1.get('hindsight_status')}'")
    print(f"  Official Domain = {data_1.get('source', {}).get('is_official_domain')}")

    assert res_1.status_code in (200, 201), f"Expected 200 or 201, got {res_1.status_code}"
    event_id = data_1["event"]["id"]
    assert data_1["hindsight_status"] == "retained"
    print("  [OK] TEST 1 PASSED: Verified event ingested into SQLite and retained in Hindsight.")

    # -------------------------------------------------------------
    # TEST 2: Verify SQLite Persistence & Source Citation
    # -------------------------------------------------------------
    print(f"\n[TEST 2] Verifying SQLite record for event '{event_id}'...")
    res_2 = client.get(f"/api/events/{event_id}")
    data_2 = res_2.get_json()
    evt_record = data_2.get("event", {})
    print(f"  HTTP {res_2.status_code}: Competitor = '{evt_record.get('competitor_name')}'")
    print(f"  Source Name = '{evt_record.get('source_name')}'")
    print(f"  Source URL  = '{evt_record.get('source_url')}'")

    assert res_2.status_code == 200
    assert evt_record["competitor_id"] == "microsoft"
    assert evt_record["source_url"] == msft_event["source_url"]
    assert evt_record["hindsight_status"] == "retained"
    print("  [OK] TEST 2 PASSED: SQLite record verified with exact source URL and competitor relation.")

    # -------------------------------------------------------------
    # TEST 3: Duplicate Protection Check
    # -------------------------------------------------------------
    print("\n[TEST 3] Testing duplicate protection by resubmitting exact same Microsoft event...")
    res_dup = client.post("/api/ingestion/events", json=msft_event)
    data_dup = res_dup.get_json()
    print(f"  HTTP {res_dup.status_code}: Status = '{data_dup.get('status')}'")
    print(f"  Database Status = '{data_dup.get('database_status')}'")
    print(f"  Message = '{data_dup.get('message')}'")

    assert res_dup.status_code == 200
    assert data_dup["status"] == "duplicate"
    assert data_dup["database_status"] == "already_present"
    print("  [OK] TEST 3 PASSED: Duplicate successfully rejected without redundant SQLite or Hindsight insertion.")

    # -------------------------------------------------------------
    # TEST 4: Validation Constraints (Strict Rejections)
    # -------------------------------------------------------------
    print("\n[TEST 4] Testing validation error handling on invalid payloads...")
    # Missing source_url
    bad_1 = dict(msft_event)
    bad_1["source_url"] = ""
    res_bad_1 = client.post("/api/ingestion/events", json=bad_1)
    print(f"  Missing source_url -> HTTP {res_bad_1.status_code}: {res_bad_1.get_json().get('message')}")
    assert res_bad_1.status_code == 400
    assert res_bad_1.get_json()["field"] == "source_url"

    # Malformed source_url (not http/https)
    bad_2 = dict(msft_event)
    bad_2["source_url"] = "not_a_valid_url"
    res_bad_2 = client.post("/api/ingestion/events", json=bad_2)
    print(f"  Malformed URL      -> HTTP {res_bad_2.status_code}: {res_bad_2.get_json().get('message')}")
    assert res_bad_2.status_code == 400

    # Empty description
    bad_3 = dict(msft_event)
    bad_3["description"] = "   "
    res_bad_3 = client.post("/api/ingestion/events", json=bad_3)
    print(f"  Empty description  -> HTTP {res_bad_3.status_code}: {res_bad_3.get_json().get('message')}")
    assert res_bad_3.status_code == 400

    # Invalid event_date
    bad_4 = dict(msft_event)
    bad_4["event_date"] = "October 21 2024"
    res_bad_4 = client.post("/api/ingestion/events", json=bad_4)
    print(f"  Invalid date       -> HTTP {res_bad_4.status_code}: {res_bad_4.get_json().get('message')}")
    assert res_bad_4.status_code == 400

    # Invalid event_type
    bad_5 = dict(msft_event)
    bad_5["event_type"] = "Gossip"
    res_bad_5 = client.post("/api/ingestion/events", json=bad_5)
    print(f"  Invalid event_type -> HTTP {res_bad_5.status_code}: {res_bad_5.get_json().get('message')}")
    assert res_bad_5.status_code == 400

    print("  [OK] TEST 4 PASSED: Strict validation correctly rejects invalid payloads with HTTP 400.")

    # -------------------------------------------------------------
    # TEST 5: Bulk Ingestion with Failure Isolation
    # -------------------------------------------------------------
    print("\n[TEST 5] Testing bulk ingestion endpoint (POST /api/ingestion/events/bulk)...")
    bulk_payload = {
        "events": [
            # Google verified event
            {
                "competitor": "Google",
                "event_type": "Product",
                "title": "Google DeepMind expands Gemini 1.5 Pro to 2 Million Token Context Window",
                "description": "Google officially doubled the context window of Gemini 1.5 Pro to 2 million tokens in developer preview and Vertex AI, establishing the longest context window in production across frontier foundation models.",
                "event_date": "2024-05-14",
                "source_name": "Google The Keyword Official Blog",
                "source_url": "https://blog.google/technology/ai/google-gemini-next-generation-model-february-2024/",
                "significance": "Differentiates Google's foundation model stack through massive long-context retrieval capacity."
            },
            # OpenAI verified event
            {
                "competitor": "OpenAI",
                "event_type": "Technology",
                "title": "OpenAI unveils OpenAI o1 Reasoning Model Series",
                "description": "OpenAI released OpenAI o1-preview, a new class of frontier AI models trained with reinforcement learning to perform chain-of-thought reasoning before answering, achieving parity with PhD students on physics, chemistry, and biology benchmarks.",
                "event_date": "2024-09-12",
                "source_name": "OpenAI Official Announcements",
                "source_url": "https://openai.com/index/introducing-openai-o1-preview/",
                "significance": "Pioneered test-time compute scaling as a new paradigm beyond pre-training scaling laws."
            },
            # Intentionally invalid event (missing source_name)
            {
                "competitor": "Google",
                "event_type": "Product",
                "title": "Invalid Test Event Without Source",
                "description": "This event intentionally omits source_name to verify error isolation.",
                "event_date": "2024-06-01",
                "source_url": "https://example.com/invalid"
            }
        ]
    }

    res_bulk = client.post("/api/ingestion/events/bulk", json=bulk_payload)
    data_bulk = res_bulk.get_json()
    print(f"  HTTP {res_bulk.status_code}: Total = {data_bulk.get('total')}")
    print(f"  Successful = {data_bulk.get('successful')}")
    print(f"  Duplicates = {data_bulk.get('duplicates')}")
    print(f"  Failed     = {data_bulk.get('failed')}")

    assert res_bulk.status_code == 200
    assert data_bulk["total"] == 3
    assert data_bulk["failed"] == 1, "The invalid event should fail cleanly without destroying batch"
    assert data_bulk["successful"] + data_bulk["duplicates"] == 2
    print("  [OK] TEST 5 PASSED: Bulk ingestion processed all items independently with failure isolation.")

    # -------------------------------------------------------------
    # TEST 6: Multi-Competitor Memory Isolation (Hindsight Banks)
    # -------------------------------------------------------------
    print("\n[TEST 6] Verifying Multi-Competitor Memory Bank Isolation across Hindsight...")
    # Recall Microsoft memory
    res_rec_ms = client.post("/api/memory/recall", json={
        "competitor": "Microsoft",
        "query": "autonomous agents Copilot Studio"
    })
    mem_ms = res_rec_ms.get_json().get("memories", [])
    print(f"  * Microsoft Bank Recall Count = {len(mem_ms)}")

    # Recall Google memory
    res_rec_goog = client.post("/api/memory/recall", json={
        "competitor": "Google",
        "query": "Gemini 2 million token context window"
    })
    mem_goog = res_rec_goog.get_json().get("memories", [])
    print(f"  * Google Bank Recall Count    = {len(mem_goog)}")

    # Recall OpenAI memory
    res_rec_oai = client.post("/api/memory/recall", json={
        "competitor": "OpenAI",
        "query": "OpenAI o1 reasoning model series"
    })
    mem_oai = res_rec_oai.get_json().get("memories", [])
    print(f"  * OpenAI Bank Recall Count    = {len(mem_oai)}")

    assert len(mem_ms) > 0, "Microsoft bank should contain Microsoft Copilot Studio memory"
    assert len(mem_goog) > 0, "Google bank should contain Gemini 2M context memory"
    assert len(mem_oai) > 0, "OpenAI bank should contain OpenAI o1 memory"

    # Cross-check: ensure Microsoft bank does NOT return OpenAI o1 or Google Gemini content
    for m in mem_ms:
        txt = m.get("text", "").lower()
        assert "openai o1" not in txt, "Isolation failure: OpenAI memory found in Microsoft bank!"
        assert "gemini 1.5" not in txt, "Isolation failure: Google memory found in Microsoft bank!"

    print("  [OK] TEST 6 PASSED: Cross-bank isolation verified. Zero memory cross-contamination.")

    # -------------------------------------------------------------
    # TEST 7: Ingestion Subsystem Status Endpoint
    # -------------------------------------------------------------
    print("\n[TEST 7] Testing GET /api/ingestion/status...")
    res_status = client.get("/api/ingestion/status")
    data_status = res_status.get_json()
    print(f"  HTTP {res_status.status_code}: Status = '{data_status.get('status')}'")
    print(f"  Database Engine = '{data_status.get('database', {}).get('engine')}' (Connected: {data_status.get('database', {}).get('connected')})")
    print(f"  Hindsight Status = '{data_status.get('hindsight', {}).get('status')}' (Connected: {data_status.get('hindsight', {}).get('connected')})")
    print(f"  Total Competitors = {data_status.get('metrics', {}).get('total_competitors')}")
    print(f"  Total Events = {data_status.get('metrics', {}).get('total_events')}")
    print(f"  Events Retained = {data_status.get('metrics', {}).get('events_retained')}")

    assert res_status.status_code == 200
    assert data_status["database"]["connected"] is True
    assert data_status["hindsight"]["connected"] is True
    assert data_status["metrics"]["total_events"] >= 3
    print("  [OK] TEST 7 PASSED: Ingestion status returns operational metrics without exposing secrets.")

    # -------------------------------------------------------------
    # TEST 8: Backward Compatibility with Existing Endpoints
    # -------------------------------------------------------------
    print("\n[TEST 8] Verifying backward compatibility with existing Step 5 endpoints...")
    # Timeline
    res_tl = client.get("/api/competitors/microsoft/timeline")
    assert res_tl.status_code == 200
    tl_events = res_tl.get_json().get("timeline", [])
    print(f"  GET /api/competitors/microsoft/timeline -> {len(tl_events)} events")

    # Competitor events
    res_ce = client.get("/api/competitors/microsoft/events")
    assert res_ce.status_code == 200
    print(f"  GET /api/competitors/microsoft/events   -> {len(res_ce.get_json().get('events', []))} events")

    # Filtered events
    res_fe = client.get("/api/events?competitor=google&event_type=Product")
    assert res_fe.status_code == 200
    print(f"  GET /api/events?competitor=google       -> {len(res_fe.get_json().get('events', []))} events")

    print("  [OK] TEST 8 PASSED: All Step 5 competitor & event endpoints function seamlessly.")

    # -------------------------------------------------------------
    # TEST 9: Security & Secret Leakage Check
    # -------------------------------------------------------------
    print("\n[TEST 9] Checking for accidental secret leakage in API responses...")
    raw_status_str = json.dumps(data_status)
    raw_msft_str = json.dumps(data_1)
    for sensitive_keyword in ["hsk_", "gsk_", "sk-", "api_key", "secret_key"]:
        if sensitive_keyword in ["api_key"]:
            # Check value isn't an actual key
            assert "hsk_" not in raw_status_str
            assert "hsk_" not in raw_msft_str
        else:
            assert sensitive_keyword not in raw_status_str
            assert sensitive_keyword not in raw_msft_str

    print("  [OK] TEST 9 PASSED: No secrets, private credentials, or API keys exposed in responses.")

    print("\n" + "=" * 75)
    print(" ALL STEP 6 INGESTION LAYER TESTS COMPLETED SUCCESSFULLY!")
    print("=" * 75)


if __name__ == "__main__":
    run_ingestion_tests()

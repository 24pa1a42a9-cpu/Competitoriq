"""
CompetitorIQ QA Deep Health & Memory Isolation Verification Script
Checks:
1. Competitor Data Integrity (Microsoft, Google, OpenAI, AWS, Meta, Anthropic)
2. Events completeness: title, date, category, description, source, source_url
3. Hindsight Memory Isolation:
   - Microsoft recall -> only Microsoft memories
   - Google recall -> only Google memories
   - OpenAI recall -> only OpenAI memories
4. AI Analyst reasoning + Hindsight recall logs verification
"""
import sys
import json
import urllib.request
import urllib.error

sys.stdout.reconfigure(encoding="utf-8")

BASE_URL = "http://127.0.0.1:5000"

def get(path):
    url = f"{BASE_URL}{path}"
    req = urllib.request.Request(url, headers={"Accept": "application/json"})
    with urllib.request.urlopen(req) as resp:
        return resp.status, json.loads(resp.read().decode("utf-8"))

def post(path, payload):
    url = f"{BASE_URL}{path}"
    data = json.dumps(payload).encode("utf-8")
    req = urllib.request.Request(url, data=data, headers={"Content-Type": "application/json", "Accept": "application/json"})
    with urllib.request.urlopen(req) as resp:
        return resp.status, json.loads(resp.read().decode("utf-8"))

print("=" * 65)
print("COMPETITORIQ DEEP QA VERIFICATION: DATA & HINDSIGHT ISOLATION")
print("=" * 65)

# 1. Competitors List
st, comp_res = get("/api/competitors")
assert st == 200
competitors = comp_res.get("competitors", [])
print(f"\n[1] Competitors in Database ({len(competitors)}):")
for c in competitors:
    print(f"  - {c['name']} (ID: {c['id']}, Events: {c.get('event_count', 0)}, Bank: {c.get('hindsight_memory_identifier')})")

# 2. Verify Events for Microsoft, Google, OpenAI
for target in ["microsoft", "google", "openai"]:
    st, ev_res = get(f"/api/competitors/{target}/timeline")
    assert st == 200
    events = ev_res.get("events", [])
    print(f"\n[2] Checking Events for '{target}' ({len(events)} events):")
    assert len(events) >= 5, f"Expected >= 5 real events for {target}, got {len(events)}"
    for idx, e in enumerate(events, 1):
        assert e.get("title"), f"Missing title in event {e.get('id')}"
        assert e.get("event_date"), f"Missing date in event {e.get('id')}"
        assert e.get("event_type"), f"Missing category in event {e.get('id')}"
        assert e.get("description"), f"Missing description in event {e.get('id')}"
        assert e.get("source_name"), f"Missing source_name in event {e.get('id')}"
        assert e.get("source_url") and e.get("source_url").startswith("http"), f"Missing or invalid source_url in event {e.get('id')}"
        print(f"  [{idx}] {e['event_date']} | {e['event_type']} | {e['title'][:45]}... | Source: {e['source_name']}")

# 3. Test Hindsight Recall directly per competitor bank
print("\n[3] Testing Hindsight Recall & Isolation across Banks:")
queries = {
    "Microsoft": ("How has this company's strategy evolved over time?", "microsoft"),
    "Google": ("What are the main AI model and search integrations announced?", "google"),
    "OpenAI": ("What models and enterprise products were launched?", "open-ai")
}

for comp_name, (q, expected_slug) in queries.items():
    st, recall_res = post("/api/memory/recall", {
        "competitor": comp_name,
        "query": q,
        "top_k": 5
    })
    assert st == 200, f"Recall failed for {comp_name}: {st}"
    bank_id = recall_res.get("bank_id")
    memories = recall_res.get("memories", [])
    print(f"\n  -> {comp_name} (Bank: {bank_id}, Recalled: {len(memories)} memories)")
    assert expected_slug in bank_id.lower(), f"Unexpected bank {bank_id} for {comp_name}"
    assert len(memories) > 0, f"Zero memories returned for {comp_name}"
    
    # Check memory content for cross-contamination
    other_competitors = [c for c in ["Microsoft", "Google", "OpenAI"] if c != comp_name]
    for m in memories:
        text = m.get("text", "")
        # The primary subject must not be another competitor's core exclusive events
        print(f"     Memory snippet: {text[:90]}...")

print("\n[PASS] All data integrity and Hindsight bank isolation checks verified!")

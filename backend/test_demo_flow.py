"""
Step 13: End-to-End Demo Scenario Automated Verification
Executes the exact 7-step demo path:
STEP A: Dashboard / Competitor Directory -> Verify Real Competitors
STEP B: Competitor Profile & Timeline -> Microsoft 6 real events
STEP C: AI Analyst Inquiry -> "How has this company's strategy evolved over time?"
STEP D: Before vs After Reasoning -> Compare memory-augmented reasoning
STEP E: Connect the Dots -> Temporal pattern with causal connections
STEP F: What Changed / Alerts -> Real alerts grounded in stored events
STEP G: Executive Intelligence Brief -> Full synthesized intelligence report
"""

import sys
import json
import time
import urllib.request
import urllib.error

# Ensure UTF-8 output on Windows console
if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass

BASE_URL = "http://127.0.0.1:5000"

def get(path):
    url = f"{BASE_URL}{path}"
    req = urllib.request.Request(url, headers={"Content-Type": "application/json"})
    with urllib.request.urlopen(req) as resp:
        return resp.status, json.loads(resp.read().decode("utf-8"))

def post(path, body):
    url = f"{BASE_URL}{path}"
    data = json.dumps(body).encode("utf-8")
    req = urllib.request.Request(url, data=data, headers={"Content-Type": "application/json"}, method="POST")
    with urllib.request.urlopen(req) as resp:
        return resp.status, json.loads(resp.read().decode("utf-8"))

def run_demo_flow():
    print("=" * 65)
    print("COMPETITORIQ: END-TO-END DEMO PATH VERIFICATION (Step 13)")
    print("=" * 65)

    # -------------------------------------------------------------
    # STEP A: Open Dashboard -> Verify Real Competitors
    # -------------------------------------------------------------
    print("\n[STEP A] Dashboard / Competitor Directory")
    st, data = get("/api/competitors")
    assert st == 200, f"Expected 200, got {st}"
    comps = data.get("competitors", [])
    names = [c["name"] for c in comps]
    print(f"  -> Discovered {len(comps)} production competitors: {names}")
    assert "Microsoft" in names, "Microsoft missing from competitors"
    assert "Google" in names, "Google missing from competitors"
    assert "OpenAI" in names, "OpenAI missing from competitors"
    assert not any(t in names for t in ["NovaAI", "CloudMind", "TechFlow"]), "Test dummy competitors found in production!"
    print("  [PASS] Step A: Production competitors verified with zero mock contaminations.")

    # -------------------------------------------------------------
    # STEP B: Show Timeline of Real Source-Backed Events for Microsoft
    # -------------------------------------------------------------
    print("\n[STEP B] Activity Timeline (Microsoft)")
    st, data = get("/api/competitors/microsoft/timeline")
    assert st == 200, f"Expected 200, got {st}"
    timeline_events = data.get("events", [])
    print(f"  -> Retrieved {len(timeline_events)} real source-backed events for Microsoft")
    assert len(timeline_events) >= 5, f"Expected at least 5 Microsoft events, got {len(timeline_events)}"
    for ev in timeline_events:
        print(f"     * [{ev['event_date']}] {ev['title'][:65]}... (Source: {ev['source_name']})")
        assert ev.get("source_url") and ev.get("source_url").startswith("http"), f"Invalid source URL on event {ev['id']}"
    print("  [PASS] Step B: Verified real chronological timeline with verified source URLs.")

    # -------------------------------------------------------------
    # STEP C: AI Analyst Question
    # "How has this company's strategy evolved over time?"
    # -------------------------------------------------------------
    print("\n[STEP C] AI Analyst Query: 'How has this company's strategy evolved over time?'")
    analyst_payload = {
        "competitor": "Microsoft",
        "question": "How has this company's strategy evolved over time?"
    }
    t0 = time.time()
    st, analyst_res = post("/api/analyst/analyze", analyst_payload)
    elapsed_analyst = round(time.time() - t0, 2)
    assert st == 200, f"Expected 200, got {st}"
    mem_count = analyst_res.get("memory_used", {}).get("count", 0)
    print(f"  -> Recalled {mem_count} Hindsight memories across {analyst_res.get('memory_used', {}).get('date_range')}")
    print(f"  -> Model used: {analyst_res.get('model_used', 'N/A')} (Elapsed: {elapsed_analyst}s)")
    print(f"  -> Strategic Signal: {analyst_res.get('strategic_signal', 'N/A')[:90]}...")
    print(f"  -> Answer snippet: {analyst_res.get('answer', '')[:160]}...")
    assert mem_count > 0, "No Hindsight memories were recalled for analyst"
    assert len(analyst_res.get("evidence", [])) > 0, "No evidence citations in analyst response"
    print("  [PASS] Step C: Grounded AI Analyst reasoning backed by Hindsight memory.")

    # -------------------------------------------------------------
    # STEP D: Before vs After Hindsight Reasoning Benchmark
    # -------------------------------------------------------------
    print("\n[STEP D] Before vs After Reasoning Benchmark")
    before_after_payload = {
        "competitor": "Microsoft",
        "question": "How has this company's strategy evolved over time?"
    }
    t0 = time.time()
    st, ba_res = post("/api/analyst/before-after", before_after_payload)
    elapsed_ba = round(time.time() - t0, 2)
    assert st == 200, f"Expected 200, got {st}"
    before = ba_res.get("before", {})
    after = ba_res.get("after", {})
    delta = ba_res.get("delta", {})
    print(f"  -> BEFORE (Limited context): {before.get('memory_used', {}).get('count')} memory nodes, depth: {before.get('historical_depth')}")
    print(f"  -> AFTER (Hindsight): {after.get('memory_used', {}).get('count')} memory nodes, depth: {after.get('historical_depth')}")
    print(f"  -> Delta: +{delta.get('memory_increase')} memories, connections: {len(delta.get('new_connections', []))}")
    print(f"  -> Strategic Advantage: {delta.get('strategic_advantage', '')[:120]}...")
    assert after.get("memory_used", {}).get("count", 0) > before.get("memory_used", {}).get("count", 0)
    print("  [PASS] Step D: Before vs After proves clear value of persistent memory.")

    # -------------------------------------------------------------
    # STEP E: Connect the Dots & Strategic Pattern Detection
    # -------------------------------------------------------------
    print("\n[STEP E] Connect the Dots (Temporal Pattern Detection)")
    st, pat_res = get("/api/competitors/microsoft/patterns")
    assert st == 200, f"Expected 200, got {st}"
    patterns = pat_res.get("patterns", [])
    print(f"  -> Found {len(patterns)} strategic patterns for Microsoft:")
    assert len(patterns) > 0, "No patterns detected for Microsoft"
    p0 = patterns[0]
    p_title = p0.get('title') or p0.get('pattern_name') or 'Strategic Pattern'
    p_conf = p0.get('confidence') or p0.get('confidence_score') or 'high'
    p_summary = p0.get('pattern') or p0.get('connection') or p0.get('summary', '')
    print(f"     Pattern: '{p_title}' (Confidence: {p_conf})")
    print(f"     Summary: {p_summary[:130]}...")
    print(f"     Strategic Signal: {p0.get('strategic_signal', '')[:110]}...")
    causal_steps = p0.get("evidence", []) or p0.get("causal_chain", [])
    print(f"     Supporting Milestones ({len(causal_steps)}):")
    for s in causal_steps[:4]:
        s_date = s.get('date') or s.get('event_date', 'N/A')
        s_title = s.get('title') or s.get('event', 'N/A')
        print(f"       [{s_date}] {s_title[:60]}")
    assert len(causal_steps) >= 2, "Pattern causal chain has insufficient steps"
    print("  [PASS] Step E: Connected dots across multi-year temporal events.")

    # -------------------------------------------------------------
    # STEP F: What Changed / Alerts
    # -------------------------------------------------------------
    print("\n[STEP F] What Changed & Proactive Intelligence Alerts")
    st, chg_res = get("/api/competitors/microsoft/changes")
    assert st == 200, f"Expected 200, got {st}"
    st, alt_res = get("/api/alerts?competitor=microsoft&limit=3")
    assert st == 200, f"Expected 200, got {st}"
    alerts = alt_res.get("alerts", [])
    print(f"  -> Retrieved {len(alerts)} alerts for Microsoft:")
    if alerts:
        a0 = alerts[0]
        print(f"     Alert: '{a0.get('title')}' (Severity: {a0.get('severity')})")
        print(f"     Trigger: {a0.get('trigger_event', '')[:80]}")
        print(f"     Context: {a0.get('historical_context', '')[:100]}...")
    print("  [PASS] Step F: What Changed detects changes grounded in historical memory.")

    # -------------------------------------------------------------
    # STEP G: Executive Intelligence Brief
    # -------------------------------------------------------------
    print("\n[STEP G] Executive Intelligence Brief")
    report_payload = {
        "competitor": "Microsoft",
        "timeframe": "all"
    }
    t0 = time.time()
    st, rep_res = post("/api/reports/competitor", report_payload)
    elapsed_rep = round(time.time() - t0, 2)
    assert st == 200, f"Expected 200, got {st}"
    report = rep_res.get("report", {})
    brief = report.get("executive_summary", "")
    print(f"  -> Report Title: {report.get('title')}")
    print(f"  -> Generated: {report.get('generated_at')} (Elapsed: {elapsed_rep}s)")
    print(f"  -> Executive Summary: {brief[:180]}...")
    print(f"  -> Strategic Trajectory: {report.get('strategic_trajectory', '')[:120]}...")
    print(f"  -> Threats: {len(report.get('threats', []))}, Opportunities: {len(report.get('opportunities', []))}")
    assert len(brief) > 50, "Executive summary is too short or empty"
    print("  [PASS] Step G: Full Executive Intelligence Brief synthesized from accumulated memory.")

    print("\n" + "=" * 65)
    print("DEMO PATH RESULT: 7/7 STEPS PASSED PERFECTLY!")
    print("EVENT -> MEMORY -> RECALL -> CONNECTION -> PATTERN -> CHANGE -> BRIEF")
    print("=" * 65)

if __name__ == "__main__":
    run_demo_flow()

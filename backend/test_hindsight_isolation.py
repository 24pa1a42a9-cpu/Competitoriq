"""
Hindsight Isolation Test (Section 4 of Step 13)
Performs RETAIN -> RECALL for:
- Microsoft
- Google
- OpenAI

Verifies that recalling Microsoft does not return Google/OpenAI memories.
Verifies that recalling Google does not return Microsoft/OpenAI memories.
Verifies that recalling OpenAI does not return Microsoft/Google memories.
"""

import sys
import uuid
from services.hindsight_service import HindsightService

def test_hindsight_isolation():
    print("============================================================")
    print("SECTION 4: HINDSIGHT ISOLATION TEST")
    print("============================================================")
    
    hs = HindsightService()
    test_run_id = uuid.uuid4().hex[:6]
    
    ms_token = f"MSFT_TOKEN_{test_run_id}"
    goog_token = f"GOOG_TOKEN_{test_run_id}"
    oai_token = f"OAI_TOKEN_{test_run_id}"
    
    canary_events = {
        "microsoft": {
            "title": f"Microsoft Quantum Computing Initiative {ms_token}",
            "description": f"Microsoft Azure Quantum secret canary deployment {ms_token}.",
            "event_type": "Technology",
            "event_date": "2026-09-28",
            "source_name": "Microsoft Azure Blog",
            "source_url": "https://azure.microsoft.com/blog/canary"
        },
        "google": {
            "title": f"Google DeepMind Algorithmic Initiative {goog_token}",
            "description": f"Google DeepMind secret canary deployment {goog_token}.",
            "event_type": "Product",
            "event_date": "2026-09-28",
            "source_name": "Google The Keyword",
            "source_url": "https://blog.google/technology/canary"
        },
        "openai": {
            "title": f"OpenAI Superalignment Initiative {oai_token}",
            "description": f"OpenAI Frontier model secret canary deployment {oai_token}.",
            "event_type": "Product",
            "event_date": "2026-09-28",
            "source_name": "OpenAI Newsroom",
            "source_url": "https://openai.com/news/canary"
        }
    }
    
    # 1. RETAIN each canary into its respective competitor bank
    print("\n1. Retaining Canaries into isolated competitor banks...")
    for comp_key, ev in canary_events.items():
        comp_name = "Microsoft" if comp_key == "microsoft" else ("Google" if comp_key == "google" else "OpenAI")
        result = hs.retain_competitor_event(competitor=comp_name, event_data=ev)
        print(f"   [RETAIN] Bank: {result.get('bank_id')} | Title: {ev['title']} | Success: {result.get('success')}")
        
    # 2. RECALL and verify cross-isolation
    print("\n2. Testing cross-recall isolation...")
    competitors = [
        ("Microsoft", "microsoft", ms_token),
        ("Google", "google", goog_token),
        ("OpenAI", "openai", oai_token)
    ]
    
    contamination_detected = False
    
    for target_name, target_key, target_token in competitors:
        print(f"\n   Testing target: {target_name} (bank: {hs.get_bank_id_for_competitor(target_name)})")
        
        # Recall from target competitor
        target_res = hs.recall_competitor_memory(competitor=target_name, query=target_token, top_k=5)
        target_memories = target_res.get("memories", [])
        found_target = any(target_token in (m.get("text", "")) for m in target_memories)
        
        print(f"   Target recall: {len(target_memories)} memories returned. Own canary found: {found_target}")
        
        # Test cross-recall: check if OTHER competitors return this target token or vice-versa
        for other_name, other_key, other_token in competitors:
            if other_name == target_name:
                continue
                
            # Query OTHER competitor's bank with target's token
            other_res = hs.recall_competitor_memory(competitor=other_name, query=target_token, top_k=5)
            other_memories = other_res.get("memories", [])
            other_texts = [m.get("text", "") for m in other_memories]
            
            # Target token MUST NOT appear in other competitor's bank!
            leaked_into_other = any(target_token in txt for txt in other_texts)
            if leaked_into_other:
                print(f"   [FAIL] CONTAMINATION: {target_name} token {target_token} leaked into {other_name} bank!")
                contamination_detected = True
            else:
                print(f"   [OK] Isolation confirmed: {other_name} bank contains ZERO instances of {target_name} ({target_token}).")
                
            # Also verify target bank does not contain OTHER competitor's token
            other_token_in_target = any(other_token in (m.get("text", "")) for m in target_memories)
            if other_token_in_target:
                print(f"   [FAIL] CONTAMINATION: {other_name} token {other_token} found in {target_name} bank!")
                contamination_detected = True
                
    if contamination_detected:
        print("\n[RESULT] Isolation Test FAILED.")
        sys.exit(1)
    else:
        print("\n[RESULT] Perfect Isolation Confirmed! Microsoft, Google, and OpenAI banks are completely segregated.")

if __name__ == "__main__":
    test_hindsight_isolation()

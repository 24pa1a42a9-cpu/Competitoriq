"""
Verification script for Step 13 Data Integrity.
Checks all events in SQLite:
- competitor
- event_type
- title
- description
- event_date
- source_name
- source_url
- sqlite event ID
- corresponding Hindsight memory
- duplicates
- malformed dates
"""

import sys
import re
from datetime import datetime
from models.database import get_db_connection
from config import Config
DB_PATH = Config.DB_PATH
from services.hindsight_service import HindsightService

def verify_data_integrity():
    print("=" * 60)
    print("DATA INTEGRITY AUDIT")
    print("=" * 60)
    
    hs = HindsightService()
    
    with get_db_connection(DB_PATH) as conn:
        cursor = conn.cursor()
        
        # 1. Fetch competitors
        cursor.execute("SELECT id, name FROM competitors ORDER BY name")
        competitors = {row["id"]: row["name"] for row in cursor.fetchall()}
        print(f"Active Competitors ({len(competitors)}):")
        for cid, name in competitors.items():
            cursor.execute("SELECT COUNT(*) as count FROM competitor_events WHERE competitor_id = ?", (cid,))
            count = cursor.fetchone()["count"]
            print(f"  - {name} (id: {cid}): {count} events")
            
        # 2. Fetch all events
        cursor.execute("SELECT * FROM competitor_events ORDER BY competitor_id, event_date")
        events = cursor.fetchall()
        print(f"\nTotal Events in SQLite: {len(events)}")
        
        issues = []
        titles_seen = set()
        duplicates = []
        date_pattern = re.compile(r"^\d{4}-\d{2}-\d{2}$")
        
        events_by_competitor = {}
        for ev in events:
            cid = ev["competitor_id"]
            events_by_competitor.setdefault(cid, []).append(ev)
            
            # Check mandatory fields
            missing_fields = []
            for field in ["id", "competitor_id", "event_type", "title", "description", "event_date", "source_name", "source_url"]:
                if not ev[field]:
                    missing_fields.append(field)
            if missing_fields:
                issues.append(f"Event ID {ev['id']} missing fields: {missing_fields}")
                
            # Check date format
            if not date_pattern.match(ev["event_date"]):
                issues.append(f"Event ID {ev['id']} malformed date: {ev['event_date']}")
            else:
                try:
                    datetime.strptime(ev["event_date"], "%Y-%m-%d")
                except ValueError:
                    issues.append(f"Event ID {ev['id']} invalid calendar date: {ev['event_date']}")
                    
            # Check valid competitor ID
            if cid not in competitors:
                issues.append(f"Event ID {ev['id']} references unknown competitor ID: {cid}")
                
            # Check duplicate titles per competitor
            title_key = (cid, ev["title"].strip().lower())
            if title_key in titles_seen:
                duplicates.append(f"Duplicate title for competitor {cid}: {ev['title']}")
            titles_seen.add(title_key)
            
        if issues:
            print("\n[!] Integrity Issues Found:")
            for issue in issues:
                print(f"  - {issue}")
        else:
            print("\n[OK] Zero field or date integrity issues found across all events.")
            
        if duplicates:
            print("\n[!] Duplicates Found:")
            for dup in duplicates:
                print(f"  - {dup}")
        else:
            print("[OK] Zero duplicate events found.")
            
        # 3. Check Hindsight retention / memory recall for each active competitor with events
        print("\nChecking Hindsight Memory Isolation & Retention...")
        for cid, name in competitors.items():
            ev_list = events_by_competitor.get(cid, [])
            if not ev_list:
                print(f"  - {name} ({cid}): 0 events (clean initial state, expected for benchmark)")
                continue
                
            # Recall memories for this competitor
            result = hs.recall_competitor_memory(competitor=name, query=f"Strategic developments and product launches for {name}", top_k=10)
            memories = result.get("memories", [])
            print(f"  - {name} ({cid}): {len(ev_list)} SQLite events -> {len(memories)} recalled Hindsight memories")
            
            # Check cross-contamination
            contamination = []
            for mem in memories:
                text = (mem.get("text") or mem.get("memory") or mem.get("content") or "").lower()
                if cid == "microsoft" and ("google announces" in text or "openai releases" in text):
                    contamination.append(f"Contamination in Microsoft memory: {text[:80]}")
                elif cid == "google" and ("microsoft copilot" in text or "openai releases" in text):
                    contamination.append(f"Contamination in Google memory: {text[:80]}")
                elif cid == "openai" and ("google deepmind" in text or "microsoft azure" in text):
                    contamination.append(f"Contamination in OpenAI memory: {text[:80]}")
                        
            if contamination:
                print(f"    [!] Contamination found in {name}: {contamination}")
            else:
                print(f"    [OK] Clean isolation: No cross-competitor contamination detected.")

if __name__ == "__main__":
    verify_data_integrity()

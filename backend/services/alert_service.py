"""
CompetitorIQ Strategic Alert & "What Changed?" Service (Step 11)
Maintains competitor checkpoints, detects newly ingested events, recalls historical
Hindsight episodic context, and synthesizes evidence-backed competitive alerts with Groq.

Flow:
New Event in SQLite / Hindsight
    ↓
Compare with Previous Competitor Checkpoint
    ↓
Identify Meaningful Changes
    ↓
Hindsight RECALL for Related Historical Memories
    ↓
Groq LLM Analyzes Strategic Significance (openai/gpt-oss-120b)
    ↓
Evidence-Grounded Alert Persisted with Duplicate Protection
    ↓
Checkpoint Updated
"""

import logging
from typing import Dict, Any, List, Optional
from datetime import datetime

from services.hindsight_service import HindsightService
from services.llm_service import LLMService, GroqServiceError
from services.database_service import DatabaseService
from services.analyst_service import AnalystValidationError, UnknownCompetitorError

logger = logging.getLogger("competitoriq.alert_service")

ALERT_SYSTEM_PROMPT = """You are CompetitorIQ, an evidence-grounded competitive intelligence analyst specializing in proactive change detection.
You receive a newly observed competitor event alongside verified historical memories retrieved from persistent Hindsight memory.

Your mandate is to evaluate whether and why this new event is strategically significant when viewed against the company's historical trajectory.

OPERATING PRINCIPLES:
1. STRICT FACTUAL ACCURACY:
   - Base your assessment strictly on the supplied new event and historical memories.
   - Do NOT invent previous events, dates, sources, or URLs.
   - Do NOT claim direct causation unless explicitly established in the evidence (use cautious language: "This new move builds on earlier activity..." or "Occurring in the same strategic period as...").

2. SEPARATION OF CONCERNS:
   - WHAT CHANGED: Exactly what was announced or observed in this new event.
   - WHY IT MATTERS: The strategic implication, market shift, or competitive leverage created by this move in light of historical context.
   - HISTORICAL CONTEXT: How this move connects to earlier moves (e.g., earlier partnerships, product releases, pricing changes, or hiring).

3. SEVERITY / ATTENTION LEVEL:
   - "High attention": Major strategic inflection, multi-quarter culmination, or high market impact.
   - "Medium attention": Meaningful tactical move with direct connection to earlier initiatives.
   - "Informational": Factual update with limited strategic disruption.

4. STRUCTURED JSON OUTPUT SCHEMA:
   Respond with a valid JSON object matching this schema:
   {
     "title": "<Concise, punchy intelligence headline for the alert>",
     "what_changed": "<1-2 sentences summarizing the verified new event>",
     "why_it_matters": "<2-3 sentences explaining strategic market implications>",
     "historical_context": "<Explanation connecting this new move to prior historical memories>",
     "severity": "High attention|Medium attention|Informational",
     "confidence": "high|medium|low"
   }
"""


class AlertService:
    """
    Manages competitor checkpoints, change detection, and proactive alert generation.
    """

    def __init__(
        self,
        db_service: Optional[DatabaseService] = None,
        hindsight_service: Optional[HindsightService] = None,
        llm_service: Optional[LLMService] = None
    ):
        self.db = db_service or DatabaseService()
        self.hindsight = hindsight_service or HindsightService()
        self.llm = llm_service or LLMService()

    def _resolve_competitor(self, competitor_query: str) -> Dict[str, Any]:
        """Resolve competitor entity from SQLite."""
        comp = self.db.get_competitor(competitor_query)
        if not comp:
            comps = self.db.list_competitors()
            for c in comps:
                if c["name"].lower() == competitor_query.lower() or c["id"].lower() == competitor_query.lower():
                    return c
            raise UnknownCompetitorError(f"Competitor '{competitor_query}' is not registered in the system.")
        return comp

    def get_changes(
        self,
        competitor: str,
        since: Optional[str] = None,
        until: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Analyse "What changed?" for a competitor:
        - If 'since' is omitted, uses the competitor's last recorded checkpoint.
        - If no checkpoint exists, initialises one and returns all events up to now.
        - Returns newly detected events categorized by event type.
        """
        comp = self._resolve_competitor(competitor)
        competitor_id = comp["id"]
        competitor_name = comp["name"]

        # Check existing checkpoint
        checkpoint = self.db.get_checkpoint(competitor_id)
        effective_since = since

        if not effective_since:
            if checkpoint and checkpoint.get("last_checked_at"):
                effective_since = checkpoint["last_checked_at"]
            else:
                # First time check: use beginning of earliest stored event or None
                effective_since = None

        new_events = self.db.list_events_since(
            competitor_id=competitor_id,
            since=effective_since,
            until=until
        )

        # Categorize changes by event_type
        by_category = {}
        for ev in new_events:
            cat = ev.get("event_type") or ev.get("category") or "Other"
            by_category[cat] = by_category.get(cat, 0) + 1

        return {
            "competitor": competitor_name,
            "competitor_id": competitor_id,
            "since": effective_since,
            "until": until or datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S"),
            "new_events": new_events,
            "event_count": len(new_events),
            "by_category": by_category,
            "last_checkpoint": checkpoint.get("last_checked_at") if checkpoint else None
        }

    def generate_alerts(
        self,
        competitor: str,
        since: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Proactively evaluates new competitor activity:
        1. Identifies events since the last checkpoint (or new un-alerted events).
        2. For each un-alerted event, checks duplicate protection.
        3. Recalls related historical episodic memories from Hindsight.
        4. Synthesizes strategic importance with Groq.
        5. Persists the alert in SQLite.
        6. Updates competitor checkpoint timestamp upon success.
        """
        comp = self._resolve_competitor(competitor)
        competitor_id = comp["id"]
        competitor_name = comp["name"]
        bank_id = comp.get("hindsight_memory_identifier") or self.hindsight.get_bank_id_for_competitor(competitor_name)

        checkpoint = self.db.get_checkpoint(competitor_id)
        effective_since = since or (checkpoint.get("last_checked_at") if checkpoint else None)

        # Retrieve events since checkpoint
        candidate_events = self.db.list_events_since(
            competitor_id=competitor_id,
            since=effective_since
        )

        unalerted_events = []
        for ev in candidate_events:
            existing = self.db.get_alert_by_event(competitor_id, ev["id"])
            if not existing:
                unalerted_events.append(ev)

        # Only on initial checkpoint (when no checkpoint existed yet) do we fall back to unalerted recent events
        if not unalerted_events and not checkpoint:
            all_recent = self.db.list_events(competitor_id=competitor_id, limit=5)
            for ev in all_recent:
                if not self.db.get_alert_by_event(competitor_id, ev["id"]):
                    unalerted_events.append(ev)

        created_alerts = []
        skipped_duplicates = 0

        # If there are no new unalerted events since last check, update checkpoint and return clean empty state
        if not unalerted_events:
            updated_checkpoint = self.db.upsert_checkpoint(competitor_id)
            return {
                "status": "success",
                "competitor": competitor_name,
                "competitor_id": competitor_id,
                "alerts_generated": 0,
                "skipped_duplicates": 0,
                "alerts": [],
                "message": "No significant new competitor activity since your last check.",
                "checkpoint": updated_checkpoint.get("last_checked_at"),
                "bank_id": bank_id
            }

        for new_ev in unalerted_events[:3]:  # Limit to 3 most important per scan
            ev_id = new_ev["id"]

            # 1. Duplicate Protection Check
            if self.db.get_alert_by_event(competitor_id, ev_id):
                skipped_duplicates += 1
                continue

            # 2. Hindsight Memory Recall for Related Historical Context
            recall_query = f"{new_ev.get('title')} {new_ev.get('description', '')}"
            logger.info(f"Recalling Hindsight context for {competitor_name} alert on event: '{new_ev.get('title')}'")
            recall_res = self.hindsight.recall_competitor_memory(
                competitor=competitor_name,
                query=recall_query,
                top_k=5
            )
            memories = recall_res.get("memories", [])

            # Extract memory dates
            dates = []
            for m in memories:
                d = m.get("occurred_start") or m.get("metadata", {}).get("event_date")
                if d:
                    dates.append(str(d).split("T")[0])

            memory_used = {
                "count": len(memories),
                "earliest": min(dates) if dates else None,
                "latest": max(dates) if dates else None
            }

            # 3. Retrieve Supporting Prior Events from SQLite for Local Grounding
            prior_events = [
                e for e in self.db.list_events(competitor_id=competitor_id, limit=6)
                if e["id"] != ev_id
            ]

            # 4. Groq LLM Importance Analysis
            user_prompt_lines = [
                f"TARGET COMPETITOR: {competitor_name}",
                "",
                "NEW OBSERVED EVENT:",
                f"- [Event ID: {ev_id}] Date: {new_ev.get('event_date')} | Category: {new_ev.get('event_type')}",
                f"  Title: {new_ev.get('title')}",
                f"  Description: {new_ev.get('description')}",
                f"  Source: {new_ev.get('source_name')} ({new_ev.get('source_url')})",
                "",
                "RECALLED HISTORICAL PERSISTENT MEMORIES FROM HINDSIGHT:"
            ]

            if memories:
                for idx, m in enumerate(memories, 1):
                    m_date = m.get("occurred_start") or m.get("metadata", {}).get("event_date") or "Unknown"
                    user_prompt_lines.append(f"- [Memory #{idx}] ({m_date}): {m.get('text', '').strip()}")
            else:
                user_prompt_lines.append("- [No prior memories recalled]")

            if prior_events:
                user_prompt_lines.append("")
                user_prompt_lines.append("SUPPORTING PRIOR EVENTS IN LOCAL DATABASE:")
                for pe in prior_events[:3]:
                    user_prompt_lines.append(f"- ({pe.get('event_date')}) {pe.get('title')}: {pe.get('description')}")

            user_prompt_lines.extend([
                "",
                "ANALYST DIRECTIVES:",
                "1. Analyze whether this new move is significant in the context of the competitor's historical trajectory.",
                "2. Formulate an evidence-grounded assessment of why it matters.",
                "3. Connect it to earlier memories without assuming uncorroborated causation.",
                "4. Emit ONLY valid JSON conforming to the requested schema."
            ])

            user_prompt = "\n".join(user_prompt_lines)

            try:
                groq_res = self.llm._execute_groq_completion(
                    system_prompt=ALERT_SYSTEM_PROMPT,
                    user_prompt=user_prompt,
                    max_tokens=1000
                )
            except Exception as e:
                logger.error(f"Groq reasoning error during alert generation: {e}")
                # Fallback to grounded template if Groq fails
                groq_res = {
                    "title": f"New {new_ev.get('event_type')} milestone detected for {competitor_name}",
                    "what_changed": new_ev.get("description") or new_ev.get("title"),
                    "why_it_matters": "Represents an observable competitive development requiring monitoring.",
                    "historical_context": f"Recalled {len(memories)} related historical memories from Hindsight.",
                    "severity": "Medium attention",
                    "confidence": "high"
                }

            # 5. Persist Alert Record in SQLite
            alert_payload = {
                "id": f"alert-{competitor_id}-{ev_id.replace('evt-', '')}",
                "competitor_id": competitor_id,
                "event_id": ev_id,
                "title": groq_res.get("title") or new_ev.get("title"),
                "what_changed": groq_res.get("what_changed") or new_ev.get("description"),
                "why_it_matters": groq_res.get("why_it_matters") or "Strategic update requiring competitive review.",
                "event_type": new_ev.get("event_type", "Product"),
                "severity": groq_res.get("severity") or "Medium attention",
                "confidence": groq_res.get("confidence") or "high",
                "historical_context": groq_res.get("historical_context") or "",
                "supporting_events": [
                    {
                        "event_id": pe.get("id"),
                        "title": pe.get("title"),
                        "date": pe.get("event_date"),
                        "event_type": pe.get("event_type")
                    } for pe in prior_events[:3]
                ],
                "memory_used": memory_used,
                "source_name": new_ev.get("source_name", "Official Corporate Blog"),
                "source_url": new_ev.get("source_url", ""),
                "status": "new"
            }

            saved_alert = self.db.create_alert(alert_payload)
            created_alerts.append(saved_alert)

        # 6. Update Checkpoint Timestamp upon Successful Processing
        updated_checkpoint = self.db.upsert_checkpoint(competitor_id)

        return {
            "status": "success",
            "competitor": competitor_name,
            "competitor_id": competitor_id,
            "alerts_generated": len(created_alerts),
            "skipped_duplicates": skipped_duplicates,
            "alerts": created_alerts,
            "checkpoint": updated_checkpoint.get("last_checked_at"),
            "bank_id": bank_id
        }

    def list_alerts(
        self,
        competitor_id: Optional[str] = None,
        status: Optional[str] = None,
        event_type: Optional[str] = None,
        limit: int = 50
    ) -> List[Dict[str, Any]]:
        """Retrieve alerts matching optional filters."""
        return self.db.list_alerts(
            competitor_id=competitor_id,
            status=status,
            event_type=event_type,
            limit=limit
        )

    def mark_read(self, alert_id: str) -> Optional[Dict[str, Any]]:
        """Set alert status to 'read'."""
        return self.db.update_alert_status(alert_id, "read")

    def mark_dismissed(self, alert_id: str) -> Optional[Dict[str, Any]]:
        """Set alert status to 'dismissed' (does not delete evidence)."""
        return self.db.update_alert_status(alert_id, "dismissed")

    def get_checkpoint_status(self, competitor_id: str) -> Dict[str, Any]:
        """Retrieve current checkpoint and unread alert count for a competitor."""
        comp = self._resolve_competitor(competitor_id)
        cp = self.db.get_checkpoint(comp["id"])
        new_alerts = self.db.list_alerts(competitor_id=comp["id"], status="new")
        return {
            "competitor": comp["name"],
            "competitor_id": comp["id"],
            "last_checked_at": cp.get("last_checked_at") if cp else None,
            "new_alerts_count": len(new_alerts)
        }

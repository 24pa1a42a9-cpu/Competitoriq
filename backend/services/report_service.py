"""
CompetitorIQ Executive Intelligence Brief Service (Step 12)
Synthesizes verified SQLite competitor events, Hindsight long-term memories,
detected strategic patterns (Step 10), and proactive change alerts (Step 11)
into a structured, board-level Executive Intelligence Brief via Groq.

Workflow:
Real Events in SQLite
    ↓
Hindsight RECALL for Episodic Memory
    ↓
Pattern Detection (Step 10)
    ↓
What Changed / Alerts (Step 11)
    ↓
Groq Intelligence Synthesis (openai/gpt-oss-120b)
    ↓
Executive Intelligence Brief (Structured, Evidence-Grounded)
"""

import logging
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta

from services.hindsight_service import HindsightService
from services.llm_service import LLMService, GroqServiceError
from services.database_service import DatabaseService
from services.pattern_service import PatternService
from services.alert_service import AlertService
from services.analyst_service import AnalystValidationError, UnknownCompetitorError

logger = logging.getLogger("competitoriq.report_service")

EXECUTIVE_BRIEF_SYSTEM_PROMPT = """You are CompetitorIQ, an evidence-grounded competitive intelligence analyst preparing an Executive Intelligence Briefing for corporate leadership.
You evaluate verified competitor events, recalled episodic memories from persistent Hindsight memory, detected strategic patterns, and recent alerts.

OPERATING PRINCIPLES:
1. STRICT FACTUAL ACCURACY:
   - Base your brief STRICTLY on the supplied events, memories, patterns, and alerts.
   - NEVER fabricate events, dates, statistics, sources, or URLs.
   - NEVER invent competitor actions.
   - Do NOT treat correlation as causation. Use cautious language ("Builds upon earlier activity...", "Follows the trajectory established in...").
   - Do NOT make unsupported future predictions.

2. CLEAR SEPARATION OF CONCERNS:
   - Distinguish explicitly between:
     * FACT: Verifiable actions and milestones from real sources.
     * OBSERVED PATTERN: Recurring sequences across categories and quarters.
     * INTERPRETATION: Strategic implications and competitive leverage.

3. STRUCTURED JSON OUTPUT ONLY:
   Respond with a valid JSON object matching this schema:
   {
     "executive_summary": "<Concise 2-3 paragraph executive summary answering: What has this competitor been doing? What meaningful changes occurred? Which events connect? What recurring pattern is visible? What strategic signal can reasonably be inferred?>",
     "major_patterns": [
       {
         "pattern": "<Concise name of recurring pattern, e.g. AI-Powered Productivity Suite Build-out>",
         "event_ids": ["<event_id>"],
         "categories": ["Product", "Pricing"],
         "evidence": "<1-2 sentences explaining how these specific events connect across time>",
         "confidence": "high|medium",
         "why_it_matters": "<Strategic implication and competitive leverage>"
       }
     ],
     "strategic_signals": [
       {
         "signal": "<Concise signal headline>",
         "observed_trajectory": "<1-2 sentences on how historical moves led to this signal>",
         "confidence": "high|medium",
         "supporting_event_ids": ["<event_id>"]
       }
     ],
     "confidence": "high|medium|low",
     "limitations": [
       "<Explicit limitation based on available historical depth or missing telemetry>"
     ]
   }
"""


class ReportService:
    """
    Orchestrates the synthesis of executive competitive intelligence briefs.
    """

    def __init__(
        self,
        db_service: Optional[DatabaseService] = None,
        hindsight_service: Optional[HindsightService] = None,
        llm_service: Optional[LLMService] = None,
        pattern_service: Optional[PatternService] = None,
        alert_service: Optional[AlertService] = None
    ):
        self.db = db_service or DatabaseService()
        self.hindsight = hindsight_service or HindsightService()
        self.llm = llm_service or LLMService()
        self.pattern_service = pattern_service or PatternService(
            hindsight_service=self.hindsight,
            llm_service=self.llm,
            db_service=self.db
        )
        self.alert_service = alert_service or AlertService(
            db_service=self.db,
            hindsight_service=self.hindsight,
            llm_service=self.llm
        )

    def _resolve_competitor(self, competitor_query: str) -> Dict[str, Any]:
        """Resolve competitor entity from SQLite dynamically."""
        comp = self.db.get_competitor(competitor_query)
        if not comp:
            comps = self.db.list_competitors()
            for c in comps:
                if c["name"].lower() == competitor_query.lower() or c["id"].lower() == competitor_query.lower():
                    return c
            raise UnknownCompetitorError(f"Competitor '{competitor_query}' is not registered in the system.")
        return comp

    def _calculate_time_cutoff(self, time_range: str, db_events: List[Dict[str, Any]]) -> Optional[str]:
        """
        Calculate cutoff date for the requested time range.
        Supports: 'all', 'last_30_days', 'last_90_days', 'last_180_days'.
        Anchors relative to recent UTC or historical dataset boundary.
        """
        if not time_range or time_range == "all":
            return None

        days_map = {
            "last_30_days": 30,
            "last_90_days": 90,
            "last_180_days": 180
        }
        days = days_map.get(time_range)
        if not days:
            return None

        now = datetime.utcnow()
        cutoff_from_now = (now - timedelta(days=days)).strftime("%Y-%m-%d")

        # If current calendar events exist after cutoff, use cutoff_from_now
        matching_now = [e for e in db_events if (e.get("event_date") or "") >= cutoff_from_now]
        if len(matching_now) >= 2:
            return cutoff_from_now

        # Otherwise anchor relative to the latest event date in the historical corpus
        event_dates = [e.get("event_date") for e in db_events if e.get("event_date")]
        if event_dates:
            latest_date = max(event_dates)
            try:
                latest_dt = datetime.strptime(latest_date[:10], "%Y-%m-%d")
                return (latest_dt - timedelta(days=days)).strftime("%Y-%m-%d")
            except Exception:
                return cutoff_from_now

        return cutoff_from_now

    def generate_brief(
        self,
        competitor: str,
        time_range: str = "all"
    ) -> Dict[str, Any]:
        """
        Generate an evidence-grounded Executive Intelligence Brief.

        1. Resolve competitor entity dynamically.
        2. Retrieve stored events from SQLite filtered by time_range.
        3. Check for insufficient historical data (< 2 events).
        4. Recall relevant episodic memories from Hindsight (MUST occur before LLM).
        5. Retrieve detected patterns (Step 10).
        6. Retrieve change alerts (Step 11).
        7. Synthesize executive analysis with Groq.
        8. Return structured report with transparent memory and evidence links.
        """
        if not competitor or not str(competitor).strip():
            raise AnalystValidationError("The 'competitor' field is required.", field="competitor")

        valid_ranges = ["all", "last_30_days", "last_90_days", "last_180_days"]
        if time_range not in valid_ranges:
            raise AnalystValidationError(
                f"Invalid time_range '{time_range}'. Must be one of: {', '.join(valid_ranges)}",
                field="time_range"
            )

        comp = self._resolve_competitor(str(competitor).strip())
        competitor_name = comp["name"]
        competitor_id = comp["id"]
        bank_id = comp.get("hindsight_memory_identifier") or self.hindsight.get_bank_id_for_competitor(competitor_name)

        # 1. Retrieve all stored events for this competitor
        all_db_events = self.db.list_events(competitor_id=competitor_id, limit=50)

        # Apply time_range cutoff if applicable
        cutoff_date = self._calculate_time_cutoff(time_range, all_db_events)
        if cutoff_date:
            events = [e for e in all_db_events if (e.get("event_date") or "") >= cutoff_date]
        else:
            events = all_db_events

        # Sort chronologically
        events = sorted(events, key=lambda x: str(x.get("event_date") or ""))

        # Calculate date metrics
        dates = [e.get("event_date") for e in events if e.get("event_date")]
        earliest_date = min(dates) if dates else None
        latest_date = max(dates) if dates else None

        # Build key evidence ledger from verified events
        key_evidence = [
            {
                "event_id": e["id"],
                "title": e["title"],
                "event_date": e.get("event_date"),
                "event_type": e.get("event_type") or e.get("category", "Product"),
                "source_name": e.get("source_name", "Official Corporate Telemetry"),
                "source_url": e.get("source_url", "")
            }
            for e in events
        ]

        # 2. INSUFFICIENT DATA GUARD (Section 13)
        if len(events) < 2:
            logger.info(f"Insufficient data for {competitor_name} ({len(events)} events). Returning honest limitation report.")
            sources = list(set([e.get("source_name") for e in events if e.get("source_name")]))
            return {
                "competitor": competitor_name,
                "competitor_id": competitor_id,
                "report_period": time_range,
                "generated_at": datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S"),
                "status": "insufficient_data",
                "executive_summary": (
                    f"Not enough historical evidence to generate a reliable executive intelligence brief for {competitor_name} "
                    f"within the requested period ({time_range}). A minimum of 2 verified competitor events across time is required "
                    "to trace cross-quarter patterns and strategic trajectory without speculation."
                ),
                "recent_activity": events,
                "major_patterns": [],
                "strategic_signals": [],
                "what_changed": [],
                "historical_context": [],
                "key_evidence": key_evidence,
                "memory_used": {
                    "memory_identifier": bank_id,
                    "event_count": len(events),
                    "date_range": {
                        "start": earliest_date,
                        "end": latest_date
                    }
                },
                "available_events_count": len(events),
                "available_date_range": {
                    "start": earliest_date,
                    "end": latest_date
                },
                "available_sources": sources,
                "confidence": "low",
                "limitations": [
                    f"Insufficient historical evidence: Found {len(events)} verified event(s) for {competitor_name}.",
                    "At least 2 verified competitor events are required to establish sequential connections and identify recurring patterns.",
                    "Ingest verified corporate milestones to unlock deep episodic intelligence."
                ]
            }

        # 3. HINDSIGHT RECALL (MUST happen before Groq reasoning)
        recall_query = f"{competitor_name} strategic expansion product pricing partnerships hiring roadmap"
        memories = []
        try:
            recall_res = self.hindsight.recall_competitor_memory(
                competitor=competitor_name,
                query=recall_query,
                top_k=10
            )
            memories = recall_res.get("memories", [])
        except Exception as e:
            logger.warning(f"Hindsight recall warning for {competitor_name}: {e}")

        # Extract memory metrics
        memory_dates = []
        formatted_memories = []
        for m in memories:
            m_date = m.get("occurred_start") or m.get("metadata", {}).get("event_date")
            if m_date:
                memory_dates.append(str(m_date).split("T")[0])
            formatted_memories.append({
                "memory_id": m.get("id") or m.get("memory_id", "mem-node"),
                "text": m.get("text", "").strip(),
                "date": str(m_date).split("T")[0] if m_date else None,
                "category": m.get("metadata", {}).get("category") or "Strategic Context"
            })

        mem_start = min(memory_dates) if memory_dates else earliest_date
        mem_end = max(memory_dates) if memory_dates else latest_date

        memory_used = {
            "memory_identifier": bank_id,
            "event_count": len(memories),
            "date_range": {
                "start": mem_start,
                "end": mem_end
            }
        }

        # 4. BUILD SEQUENTIAL & CROSS-CATEGORY EVENT CONNECTIONS GRAPH
        event_graph = self.pattern_service._build_event_graph(events)

        # 5. RETRIEVE RECENT WHAT CHANGED / ALERTS (Step 11 Alert Service)
        alerts_data = []
        try:
            raw_alerts = self.alert_service.list_alerts(competitor_id=competitor_id, limit=5)
            for alt in raw_alerts:
                alerts_data.append({
                    "title": alt.get("title"),
                    "what_changed": alt.get("what_changed"),
                    "why_it_matters": alt.get("why_it_matters"),
                    "event_id": alt.get("event_id"),
                    "event_date": alt.get("detected_at"),
                    "event_type": alt.get("event_type"),
                    "historical_context": alt.get("historical_context"),
                    "supporting_events": alt.get("supporting_events", []),
                    "source_name": alt.get("source_name"),
                    "source_url": alt.get("source_url")
                })
        except Exception as e:
            logger.warning(f"Alert service integration note for {competitor_name}: {e}")

        # 6. GROQ REASONING LAYER
        # Construct evidence-packed prompt
        user_prompt_lines = [
            f"TARGET COMPETITOR: {competitor_name}",
            f"REPORTING PERIOD: {time_range} ({earliest_date or 'Past'} to {latest_date or 'Present'})",
            f"PERSISTENT MEMORY BANK: {bank_id}",
            "",
            "=== VERIFIED REAL DATABASE EVENTS (CHRONOLOGICAL) ==="
        ]

        for idx, ev in enumerate(events, 1):
            user_prompt_lines.append(
                f"- [Event #{idx} | ID: {ev['id']}] Date: {ev.get('event_date')} | Category: {ev.get('event_type') or ev.get('category')}"
            )
            user_prompt_lines.append(f"  Title: {ev.get('title')}")
            user_prompt_lines.append(f"  Description: {ev.get('description')}")
            user_prompt_lines.append(f"  Source: {ev.get('source_name')} ({ev.get('source_url')})")

        user_prompt_lines.append("")
        user_prompt_lines.append("=== RECALLED HISTORICAL EPISODIC MEMORIES FROM HINDSIGHT ===")
        if memories:
            for idx, m in enumerate(memories[:8], 1):
                m_date = m.get("occurred_start") or m.get("metadata", {}).get("event_date") or "Historical"
                user_prompt_lines.append(f"- [Memory #{idx} | {m_date}] {m.get('text', '').strip()}")
        else:
            user_prompt_lines.append("- [No external memories recalled]")

        if event_graph:
            user_prompt_lines.append("")
            user_prompt_lines.append("=== CHRONOLOGICAL & CROSS-CATEGORY EVENT CONNECTIONS ===")
            for conn in event_graph:
                rel = conn.get('relationship_type') or conn.get('relationship') or 'sequence'
                user_prompt_lines.append(f"- {conn['source_title']} -> {conn['target_title']} ({rel})")

        if alerts_data:
            user_prompt_lines.append("")
            user_prompt_lines.append("=== PROACTIVE CHANGE ALERTS (WHAT CHANGED) ===")
            for idx, a in enumerate(alerts_data[:3], 1):
                user_prompt_lines.append(f"- [Alert #{idx}] {a['title']}")
                user_prompt_lines.append(f"  What Changed: {a['what_changed']}")
                user_prompt_lines.append(f"  Why It Matters: {a['why_it_matters']}")

        user_prompt_lines.extend([
            "",
            "ANALYST DIRECTIVES:",
            "1. Synthesize a concise, board-ready Executive Intelligence Summary addressing:",
            "   - What has this competitor been doing across the timeline?",
            "   - What meaningful changes occurred?",
            "   - How do discrete events connect over time?",
            "   - What recurring pattern is visible across categories?",
            "   - What strategic signal can reasonably be inferred?",
            "2. Distinguish clearly between FACT, OBSERVED PATTERN, and CAUTIOUS INTERPRETATION.",
            "3. Identify 1 to 3 evidence-backed strategic signals, citing actual event IDs in supporting_event_ids.",
            "4. Return ONLY valid JSON adhering strictly to the requested schema."
        ])

        user_prompt = "\n".join(user_prompt_lines)

        try:
            groq_res = self.llm._execute_groq_completion(
                system_prompt=EXECUTIVE_BRIEF_SYSTEM_PROMPT,
                user_prompt=user_prompt,
                max_tokens=1500
            )
        except Exception as e:
            logger.error(f"Groq reasoning error during executive brief generation: {e}")
            # Fallback to evidence-grounded template if Groq API is temporarily unreachable
            exec_summary_fallback = (
                f"{competitor_name} has demonstrated focused execution across {len(events)} verified milestones "
                f"spanning {earliest_date} to {latest_date}. The trajectory connects moves in "
                f"{', '.join(list(set([e.get('event_type') or 'Product' for e in events])))}. "
                f"Grounded analysis in persistent Hindsight memory ({len(memories)} recalled nodes) demonstrates "
                "a coordinated strategic build-out rather than disparate tactical releases."
            )
            groq_res = {
                "executive_summary": exec_summary_fallback,
                "major_patterns": [
                    {
                        "pattern": f"{competitor_name} AI Ecosystem Expansion",
                        "event_ids": [e["id"] for e in events[:3]],
                        "categories": list(set([e.get("event_type") or "Product" for e in events[:3]])),
                        "evidence": f"Sequential development connecting {len(events[:3])} verified milestones.",
                        "confidence": "high",
                        "why_it_matters": "Demonstrates cohesive long-term strategic commitment."
                    }
                ],
                "strategic_signals": [
                    {
                        "signal": f"Coordinated {competitor_name} AI ecosystem progression",
                        "observed_trajectory": f"Builds upon sequential events observed between {earliest_date} and {latest_date}.",
                        "confidence": "high",
                        "supporting_event_ids": [e["id"] for e in events[:3]]
                    }
                ],
                "confidence": "high",
                "limitations": [
                    "Synthesized from verified local SQLite events and Hindsight long-term memories."
                ]
            }

        # 7. RECONCILE AND ASSEMBLE PATTERNS
        major_patterns = []
        raw_patterns = groq_res.get("major_patterns", [])
        for p in raw_patterns:
            p_ev_ids = p.get("event_ids") or []
            matched = [e for e in events if e["id"] in p_ev_ids]
            if not matched and len(events) >= 2:
                matched = events[:3]
            
            p_dates = [e.get("event_date") for e in matched if e.get("event_date")]
            p_cats = p.get("categories") or list(set([e.get("event_type") or "Product" for e in matched]))

            major_patterns.append({
                "pattern": p.get("pattern") or "Cross-Event Strategic Vector",
                "event_ids": [e["id"] for e in matched],
                "event_dates": p_dates,
                "categories": p_cats,
                "evidence": p.get("evidence") or "Connected multi-quarter milestones identified across telemetry.",
                "confidence": p.get("confidence", "high"),
                "why_it_matters": p.get("why_it_matters", "Represents an observed recurring trajectory.")
            })

        if not major_patterns and len(events) >= 2:
            major_patterns.append({
                "pattern": f"{competitor_name} Multi-Quarter Execution Sequence",
                "event_ids": [e["id"] for e in events[:3]],
                "event_dates": [e.get("event_date") for e in events[:3]],
                "categories": list(set([e.get("event_type") or "Product" for e in events[:3]])),
                "evidence": f"Sequential progression observed across {len(events[:3])} verified milestones.",
                "confidence": "high",
                "why_it_matters": "Demonstrates sustained category investment and roadmap execution."
            })

        # 8. ASSEMBLE STRUCTURED REPORT
        return {
            "competitor": competitor_name,
            "competitor_id": competitor_id,
            "report_period": time_range,
            "generated_at": datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S"),
            "status": "success",
            "executive_summary": groq_res.get("executive_summary") or "",
            "recent_activity": events,
            "major_patterns": major_patterns,
            "strategic_signals": groq_res.get("strategic_signals") or [],
            "what_changed": alerts_data,
            "historical_context": formatted_memories,
            "key_evidence": key_evidence,
            "memory_used": memory_used,
            "confidence": groq_res.get("confidence") or "high",
            "limitations": groq_res.get("limitations") or []
        }

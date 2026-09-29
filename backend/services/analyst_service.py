"""
CompetitorIQ Strategic Analyst Service Layer
Coordinates Question Intent Classification, SQLite structured facts,
and Hindsight episodic memory recall with Groq LLM reasoning.

Target Architecture Flow:
User Question
    ↓
Question Understanding / Intent Classification (19 canonical intents)
    ↓
Identify Competitor(s) & Validate Parameters
    ↓
Determine Required Data Sources (SQLite profile, events, alerts, Hindsight)
    ↓
Retrieve Structured Data from SQLite when appropriate
    ↓
Hindsight RECALL when historical/contextual memory is useful
    ↓
Combine Evidence & Check Sufficiency
    ↓
Groq Strategic Reasoning (openai/gpt-oss-120b)
    ↓
Evidence-backed Professional Intelligence Synthesis with Full Transparency
"""

import logging
from typing import Dict, Any, List, Optional
from datetime import datetime

from services.hindsight_service import (
    HindsightService,
    HindsightServiceError,
    HindsightConfigError,
    HindsightConnectionError
)
from services.llm_service import (
    LLMService,
    LLMServiceError,
    GroqConfigError,
    GroqServiceError
)
from services.database_service import DatabaseService
from services.intent_service import (
    QuestionIntentClassifier,
    IntentClassification,
    INTENT_GENERAL_COMPANY_INFO,
    INTENT_COMPETITOR_COMPARISON,
    INTENT_HISTORICAL_STRATEGY,
    INTENT_STRATEGY_EVOLUTION,
    INTENT_PRICING_ANALYSIS,
    INTENT_MEMORY_QUERY
)

logger = logging.getLogger("competitoriq.analyst_service")


class AnalystValidationError(Exception):
    """Raised when incoming analysis request payload fails validation."""
    def __init__(self, message: str, field: Optional[str] = None):
        super().__init__(message)
        self.message = message
        self.field = field


class UnknownCompetitorError(Exception):
    """Raised when requested competitor does not exist in registry."""
    def __init__(self, message: str):
        super().__init__(message)
        self.message = message


class AnalystService:
    """
    Core competitive intelligence orchestrator.
    Determines required data sources based on question intent, combines
    structured SQLite facts and Hindsight memory, and drives Groq reasoning.
    """

    def __init__(
        self,
        hindsight_service: Optional[HindsightService] = None,
        llm_service: Optional[LLMService] = None,
        db_service: Optional[DatabaseService] = None
    ):
        self.hindsight = hindsight_service or HindsightService()
        self.llm = llm_service or LLMService()
        self.db = db_service or DatabaseService()
        self.intent_classifier = QuestionIntentClassifier()

    def _extract_memory_metrics(
        self,
        memories: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Calculate memory transparency metrics (count, date bounds, evidence list)."""
        dates = []
        evidence_list = []

        for mem in memories:
            date_val = mem.get("occurred_start") or mem.get("metadata", {}).get("event_date")
            clean_date = None
            if date_val:
                clean_date = str(date_val).split("T")[0]
                dates.append(clean_date)

            score_obj = mem.get("scores", {})
            relevance = score_obj.get("final") if isinstance(score_obj, dict) else None

            evidence_list.append({
                "memory_id": mem.get("id"),
                "date": clean_date,
                "category": mem.get("metadata", {}).get("category") or mem.get("type", "memory"),
                "text": mem.get("text"),
                "relevance_score": relevance,
                "source": mem.get("metadata", {}).get("source", "Hindsight Memory"),
                "source_url": mem.get("metadata", {}).get("source_url", "")
            })

        earliest = min(dates) if dates else None
        latest = max(dates) if dates else None

        return {
            "count": len(memories),
            "date_range": {
                "earliest": earliest,
                "latest": latest
            },
            "evidence": evidence_list
        }

    def analyze_competitor(
        self,
        competitor: str,
        question: str,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None,
        top_k: int = 10
    ) -> Dict[str, Any]:
        """
        Execute single-competitor intelligence synthesis:
        1. Validates inputs & checks parameters.
        2. Classifies Question Intent (19 canonical intents).
        3. Resolves target competitor in SQLite registry.
        4. Determines Required Data:
           - Retrieves structured profile facts and events from SQLite.
           - Recalls Hindsight episodic memories when historical context is useful.
        5. Combines evidence & verifies sufficiency.
        6. Groq LLM synthesizes direct, evidence-grounded strategic answers.
        7. Returns structured response with full memory transparency.
        """
        # 1. Validation
        if not competitor or not str(competitor).strip():
            raise AnalystValidationError("The 'competitor' field is required.", field="competitor")
        if not question or not str(question).strip():
            raise AnalystValidationError("The 'question' field cannot be empty.", field="question")

        comp_query = str(competitor).strip()
        question_clean = str(question).strip()

        # 2. Intent Classification
        classification: IntentClassification = self.intent_classifier.classify(
            question=question_clean,
            competitor_hint=comp_query
        )
        logger.info(
            f"Classified inquiry for '{comp_query}' as intent: {classification.intent} "
            f"(Confidence: {classification.confidence:.2f}, needs_hindsight={classification.needs_hindsight})"
        )

        # 3. Resolve competitor in SQLite database
        comp = self.db.get_competitor(comp_query)
        if not comp:
            # Check case-insensitive match across list
            comps = self.db.list_competitors()
            for c in comps:
                if c["name"].lower() == comp_query.lower() or c["id"].lower() == comp_query.lower():
                    comp = c
                    break
        if not comp:
            raise UnknownCompetitorError(
                f"Competitor '{comp_query}' is not registered in the system."
            )

        competitor_name = comp["name"]
        comp_id = comp["id"]
        bank_id = comp.get("hindsight_memory_identifier") or self.hindsight.get_bank_id_for_competitor(competitor_name)

        # 4. Structured Data Retrieval from SQLite
        db_events = []
        if classification.needs_sqlite_events:
            try:
                # If specific category requested, try fetching category-specific events first
                if classification.event_category_filter:
                    cat_events = self.db.list_events(
                        competitor_id=comp_id,
                        event_type=classification.event_category_filter,
                        start_date=start_date,
                        end_date=end_date,
                        limit=10
                    )
                    db_events.extend(cat_events)

                # Supplement with general recent events if needed
                if len(db_events) < 5:
                    general_events = self.db.list_events(
                        competitor_id=comp_id,
                        start_date=start_date,
                        end_date=end_date,
                        limit=10
                    )
                    seen_event_ids = {e["id"] for e in db_events}
                    for ge in general_events:
                        if ge["id"] not in seen_event_ids:
                            db_events.append(ge)
            except Exception as e:
                logger.warning(f"Could not retrieve local events for {competitor_name}: {e}")

        # Stored alerts if requested
        alerts = []
        if classification.needs_alerts:
            try:
                alerts = self.db.list_alerts(competitor_id=comp_id, limit=3)
            except Exception:
                alerts = []

        # Stored patterns if requested
        patterns = []
        if classification.needs_patterns:
            try:
                patterns = self.db.list_patterns(competitor_id=comp_id, limit=3)
            except Exception:
                patterns = []

        # 5. Hindsight Memory Recall (when historical/contextual memory is useful)
        memories = []
        if classification.needs_hindsight:
            search_query = classification.hindsight_query or question_clean
            logger.info(f"Recalling Hindsight memories for '{competitor_name}' on query: '{search_query}'")
            try:
                recall_res = self.hindsight.recall_competitor_memory(
                    competitor=competitor_name,
                    query=search_query,
                    top_k=top_k
                )
                memories = recall_res.get("memories", [])
            except Exception as e:
                logger.warning(
                    f"Hindsight recall could not retrieve memories for {competitor_name}: {e}. "
                    "Proceeding with available structured evidence."
                )
                memories = []

            # Filter by date range if provided
            if start_date or end_date:
                filtered = []
                for m in memories:
                    m_date = m.get("occurred_start") or m.get("metadata", {}).get("event_date")
                    if m_date:
                        m_d_str = str(m_date).split("T")[0]
                        if start_date and m_d_str < start_date:
                            continue
                        if end_date and m_d_str > end_date:
                            continue
                    filtered.append(m)
                memories = filtered
        else:
            logger.info(
                f"Skipping Hindsight recall for '{competitor_name}' as intent '{classification.intent}' "
                "is answered directly from structured corporate facts."
            )

        # 6. Memory Metrics & Evidence Extraction
        metrics = self._extract_memory_metrics(memories)

        # 7. Check for Insufficient Evidence
        has_memories = len(memories) > 0
        has_events = len(db_events) > 0
        has_profile_facts = bool(
            comp.get("hq") or comp.get("industry") or comp.get("founded") or
            comp.get("stage") or comp.get("description") or comp.get("primary_battleground")
        )

        # Honest limitation when:
        # A) Zero memories and zero events, and not an answerable company profile question
        # B) Historical/pricing inquiry requiring episodic memory where neither memory nor events exist
        is_historical_intent = classification.intent in [
            INTENT_HISTORICAL_STRATEGY,
            INTENT_STRATEGY_EVOLUTION,
            INTENT_PRICING_ANALYSIS,
            INTENT_MEMORY_QUERY
        ]
        if (not has_memories and not has_events and not (classification.intent == INTENT_GENERAL_COMPANY_INFO and has_profile_facts)) or \
           (not has_memories and not has_events and is_historical_intent):
            logger.info(f"Insufficient memory found for {competitor_name} on intent {classification.intent}. Returning structured limitation.")
            return {
                "competitor": competitor_name,
                "question": question_clean,
                "intent": classification.intent,
                "answer": f"There is insufficient stored evidence in Hindsight to answer this question for {competitor_name}.",
                "key_events": [],
                "connections": [],
                "pattern": "Insufficient Evidence",
                "strategic_signal": "No conclusive signal available from stored telemetry",
                "why_it_matters": "Strategic decisions should not be based on uncorroborated assumptions in the absence of verified competitive telemetry.",
                "confidence": "low",
                "memory_used": {
                    "count": 0,
                    "date_range": {
                        "earliest": None,
                        "latest": None
                    },
                    "earliest": None,
                    "latest": None
                },
                "memory_count": 0,
                "evidence": [],
                "limitations": [
                    f"No relevant historical memories were found in Hindsight episodic memory for {competitor_name} regarding this inquiry."
                ],
                "bank_id": bank_id
            }

        # 8. Groq LLM Strategic Reasoning
        insight = self.llm.generate_competitive_insight(
            competitor=competitor_name,
            question=question_clean,
            recalled_memories=memories,
            date_range={"start_date": start_date, "end_date": end_date},
            relevant_events=db_events,
            company_profile=comp,
            intent=classification.intent,
            alerts=alerts,
            patterns=patterns
        )

        # 9. Format Evidence Citations & Memory Transparency Metadata
        evidence_citations = list(metrics["evidence"])
        # If no Hindsight memories were recalled (e.g. general company info or pure SQLite telemetry),
        # populate evidence from verified SQLite events so Evidence Drawer has supporting items
        if not evidence_citations and db_events:
            for ev in db_events[:5]:
                evidence_citations.append({
                    "memory_id": ev.get("id"),
                    "date": ev.get("event_date"),
                    "category": ev.get("event_type") or ev.get("category", "Event"),
                    "text": f"{ev.get('title')}: {ev.get('description', '')}",
                    "relevance_score": 1.0,
                    "source": ev.get("source_name", "Verified Corporate Source"),
                    "source_url": ev.get("source_url", "")
                })

        earliest_date = metrics["date_range"]["earliest"]
        latest_date = metrics["date_range"]["latest"]
        if not earliest_date and db_events:
            ev_dates = [e.get("event_date") for e in db_events if e.get("event_date")]
            if ev_dates:
                earliest_date = min(ev_dates)
                latest_date = max(ev_dates)

        insight["competitor"] = competitor_name
        insight["question"] = question_clean
        insight["intent"] = classification.intent
        insight["sources_used"] = {
            "hindsight_memory": bool(memories),
            "sqlite_profile": True,
            "sqlite_events": bool(db_events),
            "alerts": bool(alerts),
            "patterns": bool(patterns)
        }
        insight["memory_used"] = {
            "count": metrics["count"],
            "date_range": {
                "earliest": earliest_date,
                "latest": latest_date
            },
            "earliest": earliest_date,
            "latest": latest_date
        }
        insight["memory_count"] = metrics["count"]
        insight["evidence"] = evidence_citations
        insight["bank_id"] = bank_id

        return insight

    def compare_competitors(
        self,
        competitors: List[str],
        question: str,
        top_k: int = 10
    ) -> Dict[str, Any]:
        """
        Execute multi-competitor comparison reasoning.
        Maintains strict memory isolation:
        1. Validates competitor list (at least 2 competitors, no duplicates).
        2. Recalls memories for each company independently from its isolated bank.
        3. Never merges memories across companies.
        4. Synthesizes cross-company comparison with company-specific insights,
           shared patterns, differences, and per-company memory counts.
        """
        # 1. Validation
        if not competitors or not isinstance(competitors, list):
            raise AnalystValidationError("The 'competitors' field must be an array of competitor names.", field="competitors")

        clean_comps = [str(c).strip() for c in competitors if str(c).strip()]
        # Check for at least 2 competitors
        if len(clean_comps) < 2:
            raise AnalystValidationError("At least 2 competitors are required for a comparison.", field="competitors")

        # Check for duplicates
        seen = set()
        duplicates = []
        for c in clean_comps:
            lower_c = c.lower()
            if lower_c in seen:
                duplicates.append(c)
            seen.add(lower_c)
        if duplicates:
            raise AnalystValidationError(f"Duplicate competitors detected: {', '.join(duplicates)}.", field="competitors")

        if not question or not str(question).strip():
            raise AnalystValidationError("The strategic comparison 'question' cannot be empty.", field="question")

        question_clean = str(question).strip()

        # 2. Independent Hindsight Memory Recall per Competitor
        competitors_data = {}
        memory_used_map = {}
        resolved_names = []

        for comp_query in clean_comps:
            comp = self.db.get_competitor(comp_query)
            if not comp:
                comps = self.db.list_competitors()
                for c in comps:
                    if c["name"].lower() == comp_query.lower() or c["id"].lower() == comp_query.lower():
                        comp = c
                        break
            if not comp:
                raise UnknownCompetitorError(f"Competitor '{comp_query}' is not registered in the system.")

            c_name = comp["name"]
            resolved_names.append(c_name)

            # Recall strictly from this competitor's bank
            logger.info(f"Comparison recall for '{c_name}' on query: '{question_clean}'")
            mems = []
            retrieved_bank_id = None
            try:
                recall_res = self.hindsight.recall_competitor_memory(
                    competitor=c_name,
                    query=question_clean,
                    top_k=top_k
                )
                mems = recall_res.get("memories", [])
                retrieved_bank_id = recall_res.get("bank_id")
            except Exception as e:
                logger.warning(f"Comparison Hindsight recall failed for {c_name}: {e}. Using empty memories.")
                retrieved_bank_id = self.hindsight.get_bank_id_for_competitor(c_name)

            # Corroborating local events
            c_events = []
            try:
                c_events = self.db.list_events(competitor_id=comp["id"], limit=5)
            except Exception:
                pass

            metrics = self._extract_memory_metrics(mems)

            competitors_data[c_name] = {
                "memories": mems,
                "events": c_events,
                "profile": comp,
                "metrics": metrics,
                "bank_id": retrieved_bank_id
            }

            memory_used_map[c_name] = {
                "count": metrics["count"],
                "earliest": metrics["date_range"]["earliest"],
                "latest": metrics["date_range"]["latest"]
            }

        # 3. Groq Comparative Reasoning
        comparison_result = self.llm.generate_multi_competitor_comparison(
            competitors_data=competitors_data,
            question=question_clean
        )

        # 4. Attach Verified Per-Company Memory Transparency
        comparison_result["question"] = question_clean
        comparison_result["competitors"] = resolved_names
        comparison_result["memory_used"] = memory_used_map

        return comparison_result

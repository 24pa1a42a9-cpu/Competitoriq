"""
CompetitorIQ Strategic LLM Service Layer
Integrates with the official Groq API (openai/gpt-oss-120b) to perform
evidence-grounded competitive intelligence synthesis strictly over Hindsight memories.

Core Principle:
EVENT → MEMORY → CONNECTION → PATTERN → INSIGHT
"""

import json
import logging
import re
from typing import Optional, Dict, Any, List
from config import Config

logger = logging.getLogger("competitoriq.llm")

# Primary and fallback models supported by Groq
DEFAULT_MODEL = "openai/gpt-oss-120b"
FALLBACK_MODELS = [
    "openai/gpt-oss-120b",
    "openai/gpt-oss-20b"
]

SINGLE_COMPETITOR_SYSTEM_PROMPT = """You are CompetitorIQ, an elite Strategic Competitive Intelligence Analyst.
Your mandate is to provide precise, rigorous, executive-grade competitive intelligence in direct response to the user's specific inquiry.

CORE OPERATING PRINCIPLES:
1. ANSWER THE EXACT USER QUESTION FIRST:
   - The opening sentences of your answer MUST directly and specifically address what the user actually asked.
   - Remain strictly focused on the requested competitor, topic, and timeframe.
   - Do NOT produce unrelated background or boilerplate summaries unless directly pertinent.

2. GROUNDING & EVIDENCE INTEGRITY:
   - Base all statements on the provided verified evidence: SQLite structured company profiles, verified event logs, stored alerts/patterns, and recalled Hindsight episodic memories.
   - NEVER fabricate, hallucinate, or assume events, product releases, pricing changes, executive hires, dates, sources, or URLs.
   - If the provided evidence does not contain information to answer part or all of the question, explicitly state this limitation with complete honesty (e.g., "There is insufficient stored evidence regarding...").

3. RIGOROUS DISTINCTION BETWEEN FACTS AND INFERENCE:
   - Clearly delineate between verified factual observations (what happened, dates, sources) and strategic analytical inferences.
   - Use disciplined analytical terminology for deductions: "Evidence indicates...", "This move suggests...", "The chronological pattern reflects...", "Consistent with a push toward..."
   - Never present a speculative hypothesis as an established certainty.

4. MULTI-SOURCE SYNTHESIS & DOMAIN EXPERTISE:
   - Combine structured facts (company stage, headquarters, timeline, dates, event types) with temporal context and episodic memory.
   - For GENERAL_COMPANY_INFO / profile questions: Provide clear, concise corporate identity, positioning, industry, and headquarters data directly from verified facts.
   - For RECENT_ACTIVITY / WHAT_CHANGED: Detail specific latest events, dates, and strategic significance.
   - For STRATEGY_EVOLUTION / HISTORICAL_STRATEGY / PATTERN_ANALYSIS: Trace trajectory across time, connecting multi-hop developments into a coherent strategic pattern.
   - For PRICING / PRODUCT / HIRING / TECHNOLOGY / PARTNERSHIP / ACQUISITION / MESSAGING: Deeply examine the dedicated domain with supporting citations.

5. STRUCTURED JSON OUTPUT:
   You MUST respond with a valid JSON object matching this schema:
   {
     "competitor": "<Competitor Name>",
     "question": "<User Question>",
     "intent": "<Detected Intent>",
     "answer": "<Direct, executive-grade analysis directly answering the user question>",
     "key_events": [
       {
         "event_id": "<ID or citation>",
         "date": "YYYY-MM-DD",
         "event_type": "<Product|Pricing|Hiring|Partnership|Acquisition|Messaging|Funding|Leadership|Technology|Market Expansion|Other>",
         "title": "<Event title>",
         "source": "<Source name>",
         "source_url": "<Source URL>"
       }
     ],
     "connections": [
       {
         "events": ["<event_id or title 1>", "<event_id or title 2>"],
         "relationship": "<How these events relate across time>",
         "explanation": "<Strategic reasoning connecting them>"
       }
     ],
     "pattern": "<Name and concise description of the overarching strategic pattern>",
     "strategic_signal": "<Broader market or strategic implication>",
     "why_it_matters": "<Impact on competitive positioning, pricing pressure, or enterprise adoption>",
     "confidence": "high|medium|low",
     "limitations": ["<Any caveats, data constraints, or missing information>"]
   }
"""

COMPARISON_SYSTEM_PROMPT = """You are CompetitorIQ, an evidence-grounded competitive intelligence analyst.
Your mandate is to perform cross-competitor comparative reasoning strictly using the isolated memory evidence provided for each company.

OPERATING PRINCIPLES:
1. STRICT MEMORY ISOLATION:
   - Treat each competitor's supplied evidence separately. Do NOT attribute one company's moves to another.
   - Base all company-specific insights only on the memories provided under that company's section.
   - If one company has little or no memory, state that explicitly. Never invent missing facts.

2. COMPARATIVE REASONING:
   - Identify SHARED PATTERNS (where competitors are moving in parallel or reacting to the same market forces).
   - Identify KEY DIFFERENCES (divergent strategies, differing battlegrounds, contrasting execution).
   - Synthesize how their trajectories intersect and who holds tactical leverage in which dimension.

3. STRUCTURED JSON OUTPUT:
   You MUST respond with a valid JSON object matching this schema:
   {
     "question": "<Strategic Question>",
     "competitors": ["<Company 1>", "<Company 2>"],
     "comparison": "<Comprehensive strategic synthesis comparing their approaches across time>",
     "company_insights": [
       {
         "competitor": "<Company Name>",
         "insight": "<Specific analysis of this company's strategy based on its memories>",
         "key_events": [
           {
             "event_id": "<ID or citation>",
             "date": "YYYY-MM-DD",
             "event_type": "<Category>",
             "title": "<Title>",
             "source": "<Source>"
           }
         ]
       }
     ],
     "shared_patterns": [
       "<Shared market movement or industry-wide pattern>"
     ],
     "differences": [
       "<Crucial strategic divergence between competitors>"
     ],
     "limitations": [
       "<Caveats or evidence constraints>"
     ]
   }
"""


class LLMServiceError(Exception):
    """Base exception for LLM operations."""
    def __init__(self, message: str, status_code: int = 500, details: Any = None):
        super().__init__(message)
        self.message = message
        self.status_code = status_code
        self.details = details


class GroqConfigError(LLMServiceError):
    """Raised when Groq API key is missing or invalid."""
    def __init__(self, message: str):
        super().__init__(message, status_code=503)


class GroqServiceError(LLMServiceError):
    """Raised when Groq API encounters a rate limit or gateway error."""
    def __init__(self, message: str, status_code: int = 502, details: Any = None):
        super().__init__(message, status_code=status_code, details=details)


class LLMService:
    """
    Interface for Groq high-speed LLM inference.
    Executes strategic intelligence synthesis over recalled Hindsight memories.
    """

    def __init__(
        self,
        api_key: Optional[str] = None,
        model: Optional[str] = None
    ):
        self.api_key = (api_key if api_key is not None else Config.GROQ_API_KEY).strip()
        self.model = model or Config.GROQ_MODEL or DEFAULT_MODEL
        self._client = None

    @property
    def client(self):
        """Lazily initialize and return the official Groq client."""
        if self._client is None:
            if not self.api_key:
                raise GroqConfigError("GROQ_API_KEY is not configured in backend/.env.")
            try:
                from groq import Groq
                self._client = Groq(api_key=self.api_key)
                logger.info(f"Initialized Groq client configured with model: {self.model}")
            except ImportError:
                raise LLMServiceError(
                    "The 'groq' Python package is not installed. Install via requirements.txt.",
                    status_code=500
                )
            except Exception as e:
                logger.error(f"Failed to instantiate Groq client: {e}")
                raise GroqConfigError(f"Could not initialize Groq client: {str(e)}")
        return self._client

    def is_configured(self) -> bool:
        """Check if Groq API credentials have been provided."""
        return bool(self.api_key)

    def get_status(self) -> Dict[str, Any]:
        """Returns the configuration status of the Groq LLM service."""
        configured = self.is_configured()
        return {
            "service": "Groq Strategic LLM",
            "model": self.model,
            "configured": configured,
            "has_api_key": bool(self.api_key),
            "status": "ready" if configured else "credentials_required"
        }

    def _clean_and_parse_json(self, raw_text: str) -> Dict[str, Any]:
        """Robustly parse JSON response from LLM, handling markdown code fences."""
        cleaned = raw_text.strip()
        match = re.search(r"```(?:json)?\s*(\{.*?\})\s*```", cleaned, re.DOTALL)
        if match:
            cleaned = match.group(1)
        else:
            first_brace = cleaned.find("{")
            last_brace = cleaned.rfind("}")
            if first_brace != -1 and last_brace != -1 and last_brace > first_brace:
                cleaned = cleaned[first_brace:last_brace + 1]

        try:
            return json.loads(cleaned)
        except json.JSONDecodeError as err:
            logger.warning(f"JSON parsing error: {err}. Attempting fallback structure.")
            return {
                "answer": raw_text.replace("```json", "").replace("```", "").strip(),
                "key_events": [],
                "connections": [],
                "pattern": "Analysis provided in unstructured format",
                "strategic_signal": "Extracted from narrative response",
                "why_it_matters": "Review the full analytical narrative above",
                "confidence": "medium",
                "limitations": ["Output required text cleanup"]
            }

    def _build_single_user_prompt(
        self,
        competitor: str,
        question: str,
        memories: List[Dict[str, Any]],
        date_range: Optional[Dict[str, Optional[str]]] = None,
        events: Optional[List[Dict[str, Any]]] = None,
        comparison_context: Optional[str] = None,
        company_profile: Optional[Dict[str, Any]] = None,
        intent: Optional[str] = None,
        alerts: Optional[List[Dict[str, Any]]] = None,
        patterns: Optional[List[Dict[str, Any]]] = None
    ) -> str:
        """Build analytical prompt for single-competitor intelligence synthesis."""
        lines = [
            f"TARGET COMPETITOR: {competitor}",
            f"IDENTIFIED INQUIRY INTENT: {intent or 'GENERAL_COMPETITIVE_INTELLIGENCE'}",
            f"STRATEGIC QUESTION: {question}"
        ]

        if date_range and (date_range.get("start_date") or date_range.get("end_date")):
            lines.append(f"ANALYSIS TIMEFRAME: {date_range.get('start_date', 'Any')} to {date_range.get('end_date', 'Any')}")

        if comparison_context:
            lines.append(f"STRATEGIC CONTEXT: {comparison_context}")

        lines.append("")

        # 1. Structured Corporate Profile from SQLite (Ground Truth Facts)
        if company_profile:
            lines.append("VERIFIED CORPORATE PROFILE (SQLITE GROUND TRUTH):")
            lines.append(f"  Company Name: {company_profile.get('name')}")
            if company_profile.get("tagline"):
                lines.append(f"  Tagline: {company_profile.get('tagline')}")
            if company_profile.get("industry"):
                lines.append(f"  Industry: {company_profile.get('industry')}")
            if company_profile.get("hq"):
                lines.append(f"  Headquarters: {company_profile.get('hq')}")
            if company_profile.get("founded"):
                lines.append(f"  Founded: {company_profile.get('founded')}")
            if company_profile.get("stage"):
                lines.append(f"  Corporate Stage: {company_profile.get('stage')}")
            if company_profile.get("primary_battleground"):
                lines.append(f"  Primary Battleground: {company_profile.get('primary_battleground')}")
            if company_profile.get("threat_level"):
                lines.append(f"  Threat Level: {company_profile.get('threat_level')}")
            if company_profile.get("description"):
                lines.append(f"  Overview: {company_profile.get('description')}")
            if company_profile.get("website"):
                lines.append(f"  Website: {company_profile.get('website')}")
            lines.append("")

        # 2. Structured Verified Events from SQLite
        if events:
            lines.append(f"VERIFIED CHRONOLOGICAL EVENTS (SQLITE - {len(events)} events):")
            for e_idx, ev in enumerate(events, 1):
                ev_id = ev.get("id", f"evt-{e_idx}")
                ev_date = ev.get("event_date", "Unspecified")
                ev_type = ev.get("event_type") or ev.get("category", "General")
                ev_title = ev.get("title", "")
                ev_desc = ev.get("description", "")
                ev_src = ev.get("source_name", "Verified Source")
                ev_url = ev.get("source_url", "")
                lines.append(f"  [Event #{e_idx} | ID: {ev_id}] ({ev_date}) [{ev_type}] {ev_title}")
                if ev_desc:
                    lines.append(f"    Summary: {ev_desc}")
                lines.append(f"    Source: {ev_src} | URL: {ev_url}")
            lines.append("")

        # 3. Recalled Episodic Memories from Hindsight
        lines.append(f"RECALLED HINDSIGHT HISTORICAL MEMORIES ({len(memories)} memory nodes):")
        if not memories:
            lines.append("  [NO RELEVANT MEMORIES RETURNED FROM HINDSIGHT EPISODIC STORE]")
        else:
            for idx, mem in enumerate(memories, 1):
                mem_id = mem.get("id") or f"mem-{idx}"
                date_str = mem.get("occurred_start") or mem.get("metadata", {}).get("event_date") or "Date unspecified"
                category = mem.get("metadata", {}).get("category") or mem.get("type", "Memory")
                source = mem.get("metadata", {}).get("source") or "Hindsight Memory"
                source_url = mem.get("metadata", {}).get("source_url") or ""
                text = mem.get("text", "").strip()

                lines.append(f"  [Memory #{idx} | ID: {mem_id}]")
                lines.append(f"    Date: {date_str} | Type: {category}")
                lines.append(f"    Source: {source} | URL: {source_url}")
                lines.append(f"    Evidence: {text}")
            lines.append("")

        # 4. Strategic Alerts & Patterns (if available)
        if alerts:
            lines.append("DETECTED STRATEGIC ALERTS:")
            for a in alerts[:3]:
                lines.append(f"  - Alert: {a.get('title')} ({a.get('what_changed')}) [Severity: {a.get('severity')}]")
            lines.append("")

        if patterns:
            lines.append("KNOWN STRATEGIC PATTERNS:")
            for p in patterns[:3]:
                lines.append(f"  - Pattern: {p.get('pattern_name')}: {p.get('pattern_description')}")
            lines.append("")

        lines.extend([
            "ANALYST DIRECTIVES:",
            f"1. ANSWER THE EXACT QUESTION FIRST: Open your analysis by answering '{question}' directly in the first 1-2 sentences.",
            "2. ADAPT TO INTENT: If the question asks for company facts (HQ, founding, industry, stage), state them plainly from verified profile facts. If it asks about recent events, highlight dates and releases. If it asks about strategy evolution, trace chronological connections.",
            "3. EVIDENCE GROUNDING ONLY: Ground all statements in the verified profile, events, and memories provided above. NEVER fabricate unrecorded events or citations.",
            "4. STATE LIMITATIONS HONESTLY: If the provided evidence lacks details needed to fully answer the question, clearly state this in the 'limitations' array and in your answer.",
            "5. Emit ONLY valid JSON conforming to the requested schema."
        ])

        return "\n".join(lines)

    def _execute_groq_completion(
        self,
        system_prompt: str,
        user_prompt: str,
        max_tokens: int = 2500
    ) -> Dict[str, Any]:
        """Execute chat completion with automatic model fallback."""
        if not self.is_configured():
            raise GroqConfigError("GROQ_API_KEY is not configured in backend/.env.")

        models_to_try = [self.model]
        for m in FALLBACK_MODELS:
            if m not in models_to_try:
                models_to_try.append(m)

        last_error = None

        for model_name in models_to_try:
            try:
                chat_completion = self.client.chat.completions.create(
                    messages=[
                        {"role": "system", "content": system_prompt},
                        {"role": "user", "content": user_prompt}
                    ],
                    model=model_name,
                    response_format={"type": "json_object"},
                    temperature=0.2,
                    max_tokens=max_tokens
                )

                response_text = chat_completion.choices[0].message.content or "{}"
                structured_data = self._clean_and_parse_json(response_text)
                structured_data["model_used"] = model_name
                return structured_data

            except Exception as e:
                err_str = str(e)
                logger.warning(f"Groq inference failed on model '{model_name}': {err_str}")
                last_error = e

                if "model_not_found" in err_str or "does not exist" in err_str or "decommissioned" in err_str:
                    logger.info(f"Model '{model_name}' unavailable. Attempting fallback.")
                    continue

                if "rate_limit" in err_str.lower() or "429" in err_str:
                    logger.info(f"Model '{model_name}' rate limited (429). Attempting fallback model...")
                    continue

                if "invalid_api_key" in err_str or "authentication" in err_str.lower() or "401" in err_str:
                    raise GroqServiceError(
                        message=f"Groq API authentication failed: {err_str}",
                        status_code=401,
                        details=err_str
                    )

                raise GroqServiceError(
                    message=f"Groq API error during strategic reasoning: {err_str}",
                    status_code=502,
                    details=err_str
                )

        raise GroqServiceError(
            message=f"All Groq models failed: {str(last_error)}",
            status_code=502,
            details=str(last_error)
        )

    def generate_competitive_insight(
        self,
        competitor: str,
        question: str,
        recalled_memories: List[Dict[str, Any]],
        date_range: Optional[Dict[str, Optional[str]]] = None,
        relevant_events: Optional[List[Dict[str, Any]]] = None,
        comparison_context: Optional[str] = None,
        company_profile: Optional[Dict[str, Any]] = None,
        intent: Optional[str] = None,
        alerts: Optional[List[Dict[str, Any]]] = None,
        patterns: Optional[List[Dict[str, Any]]] = None
    ) -> Dict[str, Any]:
        """
        Generate evidence-backed competitive intelligence reasoning for a single competitor.
        Accepts:
        - competitor: Name of competitor
        - question: Strategic user inquiry
        - recalled_memories: Recalled Hindsight memory items
        - date_range: Optional start/end date bounds
        - relevant_events: Optional structured database events
        - comparison_context: Optional comparison framing
        - company_profile: Optional SQLite company profile facts
        - intent: Optional classified question intent
        - alerts: Optional recent alerts
        - patterns: Optional detected patterns
        """
        if not competitor or not str(competitor).strip():
            raise ValueError("Competitor name is required.")
        if not question or not str(question).strip():
            raise ValueError("Strategic question cannot be empty.")

        # Check available evidence sources
        has_memories = bool(recalled_memories)
        has_events = bool(relevant_events)
        has_profile = bool(company_profile and any(company_profile.get(k) for k in ["hq", "industry", "founded", "stage", "description"]))

        # If zero memories, zero events, and zero profile: honest insufficient evidence
        if not has_memories and not has_events and not has_profile:
            logger.info(f"0 memories, 0 events, 0 profile for {competitor}. Returning insufficient memory response.")
            return {
                "competitor": competitor,
                "question": question,
                "intent": intent or "UNKNOWN",
                "answer": f"There is insufficient stored evidence in Hindsight to answer this question for {competitor}.",
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
                    }
                },
                "limitations": [
                    f"No relevant historical memories were found in Hindsight episodic memory for {competitor} regarding this inquiry."
                ]
            }

        # If historical/pricing/strategy evolution question but both memories and events are completely empty:
        if not has_memories and not has_events and intent in ["HISTORICAL_STRATEGY", "STRATEGY_EVOLUTION", "PRICING_ANALYSIS", "MEMORY_QUERY"]:
            logger.info(f"0 memories and 0 events for historical query on {competitor}. Returning honest limitation.")
            return {
                "competitor": competitor,
                "question": question,
                "intent": intent,
                "answer": f"There is insufficient stored evidence in Hindsight to answer this question for {competitor}.",
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
                    }
                },
                "limitations": [
                    f"No relevant historical memories were found in Hindsight episodic memory for {competitor} regarding this inquiry."
                ]
            }

        user_prompt = self._build_single_user_prompt(
            competitor=competitor,
            question=question,
            memories=recalled_memories,
            date_range=date_range,
            events=relevant_events,
            comparison_context=comparison_context,
            company_profile=company_profile,
            intent=intent,
            alerts=alerts,
            patterns=patterns
        )

        logger.info(f"Executing Groq single-competitor reasoning for {competitor} (Intent: {intent or 'UNKNOWN'}, memories: {len(recalled_memories)}, events: {len(relevant_events or [])})")
        result = self._execute_groq_completion(
            system_prompt=SINGLE_COMPETITOR_SYSTEM_PROMPT,
            user_prompt=user_prompt
        )

        # Ensure schema compliance
        result.setdefault("competitor", competitor)
        result.setdefault("question", question)
        result.setdefault("intent", intent or "GENERAL_COMPETITIVE_INTELLIGENCE")
        result.setdefault("key_events", [])
        result.setdefault("connections", [])
        result.setdefault("pattern", "Evolving Competitive Trajectory")
        result.setdefault("strategic_signal", "Strategic realignment observed across historical timeline")
        result.setdefault("why_it_matters", "Changes indicate fundamental shift in market positioning")
        result.setdefault("confidence", "high" if len(recalled_memories) >= 2 or len(relevant_events or []) >= 2 else "medium")
        result.setdefault("limitations", [])

        return result

    def generate_multi_competitor_comparison(
        self,
        competitors_data: Dict[str, Dict[str, Any]],
        question: str
    ) -> Dict[str, Any]:
        """
        Generate evidence-backed cross-competitor comparison reasoning.
        Maintains strict memory isolation by presenting each competitor's
        recalled memories under separate, isolated sections.
        """
        if not competitors_data:
            raise ValueError("Competitors data cannot be empty.")
        if not question or not str(question).strip():
            raise ValueError("Comparison question cannot be empty.")

        comp_names = list(competitors_data.keys())

        # Build isolated prompt sections
        prompt_sections = [
            f"STRATEGIC COMPARISON INQUIRY: {question}",
            f"COMPETITORS UNDER REVIEW: {', '.join(comp_names)}",
            "",
            "=== INDEPENDENT COMPETITOR MEMORY BANKS (STRICT ISOLATION) ==="
        ]

        total_memories_count = 0

        for comp_name, comp_info in competitors_data.items():
            mems = comp_info.get("memories", [])
            total_memories_count += len(mems)
            prompt_sections.append(f"\n--- COMPETITOR MEMORY BANK: {comp_name} ({len(mems)} memories) ---")

            if not mems:
                prompt_sections.append("  [NO RELEVANT MEMORIES IN HINDSIGHT FOR THIS COMPANY]")
            else:
                for idx, m in enumerate(mems, 1):
                    d = m.get("occurred_start") or m.get("metadata", {}).get("event_date") or "Date unspecified"
                    t = m.get("metadata", {}).get("category") or "General"
                    txt = m.get("text", "").strip()
                    prompt_sections.append(f"  [{comp_name} Event #{idx} | {d} | {t}]: {txt}")

        prompt_sections.extend([
            "",
            "ANALYST DIRECTIVES:",
            "1. Ground each company's insights exclusively in its own memory section.",
            "2. Identify genuine shared patterns vs key strategic differences.",
            "3. State facts accurately and avoid ungrounded generalizations.",
            "4. Return strictly valid JSON conforming to the requested schema."
        ])

        user_prompt = "\n".join(prompt_sections)
        logger.info(f"Executing Groq multi-competitor comparison for {comp_names} ({total_memories_count} total memories)")

        result = self._execute_groq_completion(
            system_prompt=COMPARISON_SYSTEM_PROMPT,
            user_prompt=user_prompt,
            max_tokens=3000
        )

        # Ensure schema compliance
        result.setdefault("question", question)
        result.setdefault("competitors", comp_names)
        result.setdefault("comparison", "Comparative analysis synthesized across recalled competitor memories.")
        result.setdefault("company_insights", [])
        result.setdefault("shared_patterns", [])
        result.setdefault("differences", [])
        result.setdefault("limitations", [])

        return result

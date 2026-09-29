"""
CompetitorIQ Question Intent Classification Service
Lightweight, deterministic intent classification layer for competitive intelligence inquiries.

Identifies user intent, detects target competitors, determines required data sources,
and avoids unnecessary Hindsight calls for questions that can be answered from
structured SQLite facts or profile telemetry.

Supported Canonical Intents (19 total):
- GENERAL_COMPANY_INFO
- RECENT_ACTIVITY
- HISTORICAL_STRATEGY
- PRODUCT_ANALYSIS
- PRICING_ANALYSIS
- HIRING_ANALYSIS
- PARTNERSHIP_ANALYSIS
- ACQUISITION_ANALYSIS
- TECHNOLOGY_ANALYSIS
- MESSAGING_ANALYSIS
- STRATEGY_EVOLUTION
- COMPETITOR_COMPARISON
- EVENT_EXPLANATION
- PATTERN_ANALYSIS
- WHAT_CHANGED
- EXECUTIVE_SUMMARY
- MEMORY_QUERY
- GENERAL_COMPETITIVE_INTELLIGENCE
- UNKNOWN
"""

import re
import logging
from typing import Dict, Any, List, Optional
from dataclasses import dataclass, field

logger = logging.getLogger("competitoriq.intent_service")


@dataclass
class IntentClassification:
    """Structured result from intent classification."""
    intent: str
    confidence: float
    detected_competitors: List[str] = field(default_factory=list)
    needs_hindsight: bool = True
    needs_sqlite_events: bool = True
    needs_sqlite_profile: bool = True
    needs_alerts: bool = False
    needs_patterns: bool = False
    event_category_filter: Optional[str] = None
    hindsight_query: str = ""
    rationale: str = ""

    def to_dict(self) -> Dict[str, Any]:
        return {
            "intent": self.intent,
            "confidence": self.confidence,
            "detected_competitors": self.detected_competitors,
            "needs_hindsight": self.needs_hindsight,
            "needs_sqlite_events": self.needs_sqlite_events,
            "needs_sqlite_profile": self.needs_sqlite_profile,
            "needs_alerts": self.needs_alerts,
            "needs_patterns": self.needs_patterns,
            "event_category_filter": self.event_category_filter,
            "hindsight_query": self.hindsight_query,
            "rationale": self.rationale
        }


# Canonical Intent Definitions
INTENT_GENERAL_COMPANY_INFO = "GENERAL_COMPANY_INFO"
INTENT_RECENT_ACTIVITY = "RECENT_ACTIVITY"
INTENT_HISTORICAL_STRATEGY = "HISTORICAL_STRATEGY"
INTENT_PRODUCT_ANALYSIS = "PRODUCT_ANALYSIS"
INTENT_PRICING_ANALYSIS = "PRICING_ANALYSIS"
INTENT_HIRING_ANALYSIS = "HIRING_ANALYSIS"
INTENT_PARTNERSHIP_ANALYSIS = "PARTNERSHIP_ANALYSIS"
INTENT_ACQUISITION_ANALYSIS = "ACQUISITION_ANALYSIS"
INTENT_TECHNOLOGY_ANALYSIS = "TECHNOLOGY_ANALYSIS"
INTENT_MESSAGING_ANALYSIS = "MESSAGING_ANALYSIS"
INTENT_STRATEGY_EVOLUTION = "STRATEGY_EVOLUTION"
INTENT_COMPETITOR_COMPARISON = "COMPETITOR_COMPARISON"
INTENT_EVENT_EXPLANATION = "EVENT_EXPLANATION"
INTENT_PATTERN_ANALYSIS = "PATTERN_ANALYSIS"
INTENT_WHAT_CHANGED = "WHAT_CHANGED"
INTENT_EXECUTIVE_SUMMARY = "EXECUTIVE_SUMMARY"
INTENT_MEMORY_QUERY = "MEMORY_QUERY"
INTENT_GENERAL_CI = "GENERAL_COMPETITIVE_INTELLIGENCE"
INTENT_UNKNOWN = "UNKNOWN"

ALL_INTENTS = [
    INTENT_GENERAL_COMPANY_INFO,
    INTENT_RECENT_ACTIVITY,
    INTENT_HISTORICAL_STRATEGY,
    INTENT_PRODUCT_ANALYSIS,
    INTENT_PRICING_ANALYSIS,
    INTENT_HIRING_ANALYSIS,
    INTENT_PARTNERSHIP_ANALYSIS,
    INTENT_ACQUISITION_ANALYSIS,
    INTENT_TECHNOLOGY_ANALYSIS,
    INTENT_MESSAGING_ANALYSIS,
    INTENT_STRATEGY_EVOLUTION,
    INTENT_COMPETITOR_COMPARISON,
    INTENT_EVENT_EXPLANATION,
    INTENT_PATTERN_ANALYSIS,
    INTENT_WHAT_CHANGED,
    INTENT_EXECUTIVE_SUMMARY,
    INTENT_MEMORY_QUERY,
    INTENT_GENERAL_CI,
    INTENT_UNKNOWN
]

# Known Competitor Aliases for text entity detection
KNOWN_COMPETITOR_PATTERNS = {
    "microsoft": r"\b(microsoft|msft|azure)\b",
    "google": r"\b(google|alphabet|deepmind|gemini)\b",
    "openai": r"\b(openai|chatgpt)\b",
    "anthropic": r"\b(anthropic|claude)\b",
    "meta": r"\b(meta|facebook|llama)\b",
    "amazon / aws": r"\b(amazon|aws|bedrock)\b",
    "novaai": r"\b(novaai|nova)\b",
    "cloudmind": r"\b(cloudmind)\b",
    "techflow": r"\b(techflow)\b"
}


class QuestionIntentClassifier:
    """
    Lightweight rule-based and regex-grounded classifier for CI inquiries.
    Determines intent and selects the optimal combination of data sources.
    """

    def __init__(self, known_competitors: Optional[List[Dict[str, Any]]] = None):
        self.known_competitors = known_competitors or []

    def extract_competitors(self, text: str) -> List[str]:
        """Detect competitor mentions in free text."""
        detected = []
        text_lower = text.lower()
        for comp_name, pattern in KNOWN_COMPETITOR_PATTERNS.items():
            if re.search(pattern, text_lower):
                detected.append(comp_name)
        return detected

    def classify(
        self,
        question: str,
        competitor_hint: Optional[str] = None
    ) -> IntentClassification:
        """
        Classifies the user question into a canonical intent and determines
        the appropriate data retrieval strategy.
        """
        q_raw = question.strip()
        q_lower = q_raw.lower()

        # 1. Detect competitor mentions
        detected = self.extract_competitors(q_raw)
        if competitor_hint and competitor_hint.lower() not in [d.lower() for d in detected]:
            detected.append(competitor_hint)

        # 2. Check for Multi-Competitor Comparison
        # e.g., "compare microsoft and google", "microsoft vs google", "difference between X and Y"
        is_comparison = (
            len(detected) >= 2 or
            bool(re.search(r"\b(compare|comparison|versus|\bvs\b|differ|difference|between|head-to-head)\b", q_lower))
        )
        if is_comparison and (len(detected) >= 2 or "compare" in q_lower or " vs " in q_lower):
            return IntentClassification(
                intent=INTENT_COMPETITOR_COMPARISON,
                confidence=0.95 if len(detected) >= 2 else 0.85,
                detected_competitors=detected,
                needs_hindsight=True,
                needs_sqlite_events=True,
                needs_sqlite_profile=True,
                needs_alerts=False,
                needs_patterns=True,
                hindsight_query=q_raw,
                rationale="Comparison question detected between competitors."
            )

        # 3. Check for Memory Query
        # e.g. "what is in hindsight memory?", "recall memories", "stored episodic nodes"
        if re.search(r"\b(hindsight|episodic memory|memory bank|stored memories|recall memory|in memory)\b", q_lower):
            return IntentClassification(
                intent=INTENT_MEMORY_QUERY,
                confidence=0.92,
                detected_competitors=detected,
                needs_hindsight=True,
                needs_sqlite_events=False,
                needs_sqlite_profile=True,
                hindsight_query=q_raw,
                rationale="Direct inquiry regarding persistent Hindsight memory store."
            )

        # 4. Check for Event Explanation (e.g. "why did they...", "explain why...", "what happened with...")
        # Checked early so "Why did they launch..." is recognized as an event explanation rather than product analysis
        if re.search(r"\b(why did (they|[a-z0-9_-]+)|explain why|what happened with|details on the launch of)\b", q_lower):
            return IntentClassification(
                intent=INTENT_EVENT_EXPLANATION,
                confidence=0.92,
                detected_competitors=detected,
                needs_hindsight=True,
                needs_sqlite_events=True,
                needs_sqlite_profile=True,
                hindsight_query=q_raw,
                rationale="Explanation requested for a specific competitor action or event."
            )

        # 5. Check for "What Changed?" / Checkpoint Delta
        # e.g., "what changed?", "any new changes since last week?", "what is new since yesterday?"
        if re.search(r"\b(what('s| has| have)? changed|any changes|what is new|since last|recent changes|what's different)\b", q_lower):
            return IntentClassification(
                intent=INTENT_WHAT_CHANGED,
                confidence=0.90,
                detected_competitors=detected,
                needs_hindsight=True,
                needs_sqlite_events=True,
                needs_sqlite_profile=True,
                needs_alerts=True,
                needs_patterns=False,
                hindsight_query=f"Recent developments and strategic changes: {q_raw}",
                rationale="User inquiring about incremental developments or recent changes."
            )

        # 6. Check for Executive Summary / Briefing
        # e.g., "give me an executive summary", "briefing on microsoft", "leadership memo"
        if re.search(r"\b(executive summary|briefing|executive brief|leadership summary|overview memo|high-level summary)\b", q_lower):
            return IntentClassification(
                intent=INTENT_EXECUTIVE_SUMMARY,
                confidence=0.92,
                detected_competitors=detected,
                needs_hindsight=True,
                needs_sqlite_events=True,
                needs_sqlite_profile=True,
                needs_alerts=True,
                needs_patterns=True,
                hindsight_query=f"Strategic trajectory and major competitive initiatives: {q_raw}",
                rationale="Executive summary requested requiring cross-functional synthesis."
            )

        # 7. Check for Pattern Analysis / Behavioral Vectors / Connect the Dots
        # e.g., "what patterns do you see?", "connect the dots", "behavioral vector", "recurring pattern"
        if re.search(r"\b(pattern|patterns|connect the dots|behavioral vector|recurring|trend|trajectory pattern)\b", q_lower):
            return IntentClassification(
                intent=INTENT_PATTERN_ANALYSIS,
                confidence=0.90,
                detected_competitors=detected,
                needs_hindsight=True,
                needs_sqlite_events=True,
                needs_sqlite_profile=True,
                needs_patterns=True,
                hindsight_query=q_raw,
                rationale="Pattern analysis and strategic connect-the-dots requested."
            )

        # 8. Check for Specific Functional Domain Analysis BEFORE broad generic strategy evolution
        # Domain: Pricing Analysis
        if re.search(r"\b(price|pricing|tier|cost|subscription|discount|monetization|pricing model|fee|rate)\b", q_lower):
            return IntentClassification(
                intent=INTENT_PRICING_ANALYSIS,
                confidence=0.92,
                detected_competitors=detected,
                needs_hindsight=True,
                needs_sqlite_events=True,
                needs_sqlite_profile=True,
                event_category_filter="Pricing",
                hindsight_query=f"Pricing strategy, adjustments, enterprise tier changes: {q_raw}",
                rationale="Inquiry focused on commercial pricing strategy and adjustments."
            )

        # Domain: Hiring / Leadership Analysis
        if re.search(r"\b(hire|hiring|recruiting|talent|headcount|executive|ceo|cto|leadership|vp |resignation|staffing)\b", q_lower):
            return IntentClassification(
                intent=INTENT_HIRING_ANALYSIS,
                confidence=0.91,
                detected_competitors=detected,
                needs_hindsight=True,
                needs_sqlite_events=True,
                needs_sqlite_profile=True,
                event_category_filter="Hiring",
                hindsight_query=f"Executive hiring, talent acquisition, leadership changes: {q_raw}",
                rationale="Inquiry focused on talent acquisition and leadership movement."
            )

        # Domain: Partnership / Alliances Analysis
        if re.search(r"\b(partners?|partnerships?|alliances?|collaboration|joint venture|agreement|deal with)\b", q_lower):
            return IntentClassification(
                intent=INTENT_PARTNERSHIP_ANALYSIS,
                confidence=0.91,
                detected_competitors=detected,
                needs_hindsight=True,
                needs_sqlite_events=True,
                needs_sqlite_profile=True,
                event_category_filter="Partnership",
                hindsight_query=f"Strategic partnerships, commercial alliances, co-development: {q_raw}",
                rationale="Inquiry focused on external alliances and strategic partnerships."
            )

        # Domain: Acquisition / M&A Analysis
        if re.search(r"\b(acquisitions?|acquired|acquire|merger|buyout|purchased company|takeover)\b", q_lower):
            return IntentClassification(
                intent=INTENT_ACQUISITION_ANALYSIS,
                confidence=0.92,
                detected_competitors=detected,
                needs_hindsight=True,
                needs_sqlite_events=True,
                needs_sqlite_profile=True,
                event_category_filter="Acquisition",
                hindsight_query=f"Corporate acquisitions, mergers, and asset purchases: {q_raw}",
                rationale="Inquiry focused on corporate acquisitions and M&A transactions."
            )

        # Domain: Messaging / Branding / Narrative Analysis
        if re.search(r"\b(messaging|positioning|narrative|brand|branding|marketing campaign|pitch|pr statement)\b", q_lower):
            return IntentClassification(
                intent=INTENT_MESSAGING_ANALYSIS,
                confidence=0.90,
                detected_competitors=detected,
                needs_hindsight=True,
                needs_sqlite_events=True,
                needs_sqlite_profile=True,
                event_category_filter="Messaging",
                hindsight_query=f"Corporate positioning, key messaging, strategic narrative: {q_raw}",
                rationale="Inquiry focused on market positioning and communication narrative."
            )

        # Domain: Technology / Architecture / Silicon Analysis
        if re.search(r"\b(technology|tech stack|architecture|model|foundation model|silicon|chip|chips|hardware|infrastructure|patents?|gpu|tpu|neural|quantum)\b", q_lower):
            return IntentClassification(
                intent=INTENT_TECHNOLOGY_ANALYSIS,
                confidence=0.89,
                detected_competitors=detected,
                needs_hindsight=True,
                needs_sqlite_events=True,
                needs_sqlite_profile=True,
                event_category_filter="Technology",
                hindsight_query=f"Technology architecture, foundation models, infrastructure: {q_raw}",
                rationale="Inquiry focused on technical architecture, models, or hardware/silicon."
            )

        # Domain: Product / Feature / Tool Analysis
        if re.search(r"\b(products?|launched?|releases?|features?|offerings?|platform|service|tools?|roadmap)\b", q_lower):
            return IntentClassification(
                intent=INTENT_PRODUCT_ANALYSIS,
                confidence=0.89,
                detected_competitors=detected,
                needs_hindsight=True,
                needs_sqlite_events=True,
                needs_sqlite_profile=True,
                event_category_filter="Product",
                hindsight_query=f"Product announcements, capability releases, platform features: {q_raw}",
                rationale="Inquiry focused on product offerings, releases, and feature rollout."
            )

        # 9. Strategy Evolution / Pivot (broad changes across time)
        if re.search(r"\b(evolve|evolved|evolution|pivot|pivoted|shifted|strategic shift|direction changed|trajectory over time)\b", q_lower):
            return IntentClassification(
                intent=INTENT_STRATEGY_EVOLUTION,
                confidence=0.93,
                detected_competitors=detected,
                needs_hindsight=True,
                needs_sqlite_events=True,
                needs_sqlite_profile=True,
                needs_patterns=True,
                hindsight_query=q_raw,
                rationale="Inquiry into temporal evolution of strategic approach."
            )

        # 10. Historical Strategy
        if re.search(r"\b(history|historical|long-term|over the past (years|months)|past strategy|origin of)\b", q_lower):
            return IntentClassification(
                intent=INTENT_HISTORICAL_STRATEGY,
                confidence=0.88,
                detected_competitors=detected,
                needs_hindsight=True,
                needs_sqlite_events=True,
                needs_sqlite_profile=True,
                hindsight_query=q_raw,
                rationale="Historical strategic context requested across extensive timeline."
            )

        # 11. Competitive Intelligence Focus: Battleground, Threat Level, Stance (check BEFORE general company info)
        if re.search(r"\b(threat level|threat|battleground|competitive advantage|moat|position in the market|market share|strengths|weaknesses)\b", q_lower):
            return IntentClassification(
                intent=INTENT_GENERAL_CI,
                confidence=0.90,
                detected_competitors=detected,
                needs_hindsight=True,
                needs_sqlite_events=True,
                needs_sqlite_profile=True,
                hindsight_query=q_raw,
                rationale="General competitive intelligence assessment across battleground and threat level."
            )

        # 12. Recent Activity / Latest Moves
        if re.search(r"\b(recent|recently|latest|latest moves|current moves|newest|what are they doing now)\b", q_lower):
            return IntentClassification(
                intent=INTENT_RECENT_ACTIVITY,
                confidence=0.89,
                detected_competitors=detected,
                needs_hindsight=True,
                needs_sqlite_events=True,
                needs_sqlite_profile=True,
                needs_alerts=True,
                hindsight_query=f"Recent announcements and latest actions: {q_raw}",
                rationale="Inquiry focused on recent operational or market activity."
            )

        # 13. General Company Info / Corporate Profile Facts
        # e.g., "who is Microsoft?", "tell me about Google", "where is Anthropic based?", "when was OpenAI founded?", "what is their tagline?"
        if re.search(r"\b(who is|who are|tell me about|overview of|headquartered|headquarters|founded|where is|based in|tagline|stage|market cap|arr estimate|employee count|industry)\b", q_lower) or (
            re.search(r"^what is\b", q_lower) and not re.search(r"\b(threat|battleground|strategy|pattern|history|new|pricing|product)\b", q_lower)
        ):
            return IntentClassification(
                intent=INTENT_GENERAL_COMPANY_INFO,
                confidence=0.92,
                detected_competitors=detected,
                needs_hindsight=False,  # Primary answers come directly from SQLite profile!
                needs_sqlite_events=True,
                needs_sqlite_profile=True,
                hindsight_query=f"Corporate background and foundational profile: {q_raw}",
                rationale="General company profile question answerable from structured corporate facts."
            )

        # Fallback: UNKNOWN intent
        # Default to combining structured SQLite facts and Hindsight memory to provide best grounded answer
        return IntentClassification(
            intent=INTENT_UNKNOWN,
            confidence=0.50,
            detected_competitors=detected,
            needs_hindsight=True,
            needs_sqlite_events=True,
            needs_sqlite_profile=True,
            hindsight_query=q_raw,
            rationale="Unclassified inquiry; querying both structured facts and episodic memory."
        )

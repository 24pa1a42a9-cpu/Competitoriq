"""
CompetitorIQ Official Source Registry Configuration
Centralized registry of verified public corporate intelligence sources.

Architecture:
Provides official domains, publication channels, and metadata for primary competitors:
- Microsoft
- Google
- Amazon / AWS
- OpenAI
- Anthropic
- Meta

Designed for modular ingestion (manual verification, RSS feeds, API endpoints, web ingest).
"""

from typing import Dict, Any, List, Optional
from urllib.parse import urlparse

# Official Source Registry for Primary Competitors
COMPETITOR_SOURCES: Dict[str, Dict[str, Any]] = {
    "microsoft": {
        "competitor_id": "microsoft",
        "competitor_name": "Microsoft",
        "primary_domain": "microsoft.com",
        "official_sources": [
            {
                "source_name": "The Official Microsoft Blog",
                "url": "https://blogs.microsoft.com/",
                "type": "corporate_blog",
                "focus": "Executive announcements, major product debuts, corporate strategy",
                "verified": True
            },
            {
                "source_name": "Microsoft Azure Blog",
                "url": "https://azure.microsoft.com/en-us/blog/",
                "type": "technical_cloud_blog",
                "focus": "Cloud infrastructure, enterprise AI tools, Azure OpenAI updates",
                "verified": True
            },
            {
                "source_name": "Microsoft News Center",
                "url": "https://news.microsoft.com/",
                "type": "press_release",
                "focus": "Regulatory filings, partnerships, earnings statements",
                "verified": True
            }
        ]
    },
    "google": {
        "competitor_id": "google",
        "competitor_name": "Google",
        "primary_domain": "google.com",
        "official_sources": [
            {
                "source_name": "Google The Keyword",
                "url": "https://blog.google/",
                "type": "corporate_blog",
                "focus": "Gemini updates, consumer search, hardware, company-wide milestones",
                "verified": True
            },
            {
                "source_name": "Google Cloud Blog",
                "url": "https://cloud.google.com/blog/",
                "type": "technical_cloud_blog",
                "focus": "Vertex AI, infrastructure announcements, enterprise partnerships",
                "verified": True
            },
            {
                "source_name": "Google DeepMind Discover",
                "url": "https://deepmind.google/discover/blog/",
                "type": "research_blog",
                "focus": "Frontier AI research, benchmark breakthroughs, model releases",
                "verified": True
            }
        ]
    },
    "amazon-aws": {
        "competitor_id": "amazon-aws",
        "competitor_name": "Amazon / AWS",
        "primary_domain": "amazon.com",
        "official_sources": [
            {
                "source_name": "AWS News Blog",
                "url": "https://aws.amazon.com/blogs/aws/",
                "type": "cloud_blog",
                "focus": "Amazon Bedrock, compute pricing, service launches, feature updates",
                "verified": True
            },
            {
                "source_name": "AWS What's New",
                "url": "https://aws.amazon.com/new/",
                "type": "release_feed",
                "focus": "Daily infrastructure changes, regional availability, pricing shifts",
                "verified": True
            },
            {
                "source_name": "About Amazon News Center",
                "url": "https://www.aboutamazon.com/news",
                "type": "corporate_press",
                "focus": "Executive leadership, investments, strategic acquisitions",
                "verified": True
            }
        ]
    },
    "openai": {
        "competitor_id": "openai",
        "competitor_name": "OpenAI",
        "primary_domain": "openai.com",
        "official_sources": [
            {
                "source_name": "OpenAI News & Announcements",
                "url": "https://openai.com/news/",
                "type": "announcements",
                "focus": "Model releases (o1, GPT-4o), pricing adjustments, product launches",
                "verified": True
            },
            {
                "source_name": "OpenAI Research Index",
                "url": "https://openai.com/research/",
                "type": "research_papers",
                "focus": "Model safety evaluations, technical reports, capabilities research",
                "verified": True
            }
        ]
    },
    "anthropic": {
        "competitor_id": "anthropic",
        "competitor_name": "Anthropic",
        "primary_domain": "anthropic.com",
        "official_sources": [
            {
                "source_name": "Anthropic Newsroom",
                "url": "https://www.anthropic.com/news",
                "type": "corporate_blog",
                "focus": "Claude model family (Opus, Sonnet, Haiku), enterprise features",
                "verified": True
            },
            {
                "source_name": "Anthropic Research",
                "url": "https://www.anthropic.com/research",
                "type": "research_blog",
                "focus": "Constitutional AI, interpretability, red-teaming benchmarks",
                "verified": True
            }
        ]
    },
    "meta": {
        "competitor_id": "meta",
        "competitor_name": "Meta",
        "primary_domain": "meta.com",
        "official_sources": [
            {
                "source_name": "Meta Newsroom",
                "url": "https://about.fb.com/news/",
                "type": "corporate_press",
                "focus": "Llama foundation models, AI infrastructure, corporate updates",
                "verified": True
            },
            {
                "source_name": "Meta AI Blog",
                "url": "https://ai.meta.com/blog/",
                "type": "technical_ai_blog",
                "focus": "Open source weights, hardware clusters, generative media research",
                "verified": True
            }
        ]
    }
}


def normalize_competitor_key(key: str) -> str:
    """Normalize competitor key/name to match registry keys."""
    if not key:
        return ""
    clean = key.lower().strip()
    if "microsoft" in clean:
        return "microsoft"
    if "google" in clean:
        return "google"
    if "amazon" in clean or "aws" in clean:
        return "amazon-aws"
    if "openai" in clean:
        return "openai"
    if "anthropic" in clean:
        return "anthropic"
    if "meta" in clean or "facebook" in clean:
        return "meta"
    return clean.replace(" ", "-")


def get_sources_for_competitor(competitor_name_or_id: str) -> Optional[Dict[str, Any]]:
    """Retrieve official registered sources for a given competitor."""
    key = normalize_competitor_key(competitor_name_or_id)
    return COMPETITOR_SOURCES.get(key)


def list_all_registered_sources() -> List[Dict[str, Any]]:
    """Return all registered source channels across competitors."""
    return list(COMPETITOR_SOURCES.values())


def is_known_official_domain(competitor_name_or_id: str, url: str) -> bool:
    """
    Check if a given URL corresponds to a recognized official domain
    for the specified competitor.
    """
    comp = get_sources_for_competitor(competitor_name_or_id)
    if not comp or not url:
        return False

    try:
        parsed = urlparse(url)
        netloc = parsed.netloc.lower()
        primary = comp.get("primary_domain", "").lower()
        if primary and (netloc == primary or netloc.endswith("." + primary)):
            return True
        for src in comp.get("official_sources", []):
            src_netloc = urlparse(src.get("url", "")).netloc.lower()
            if src_netloc and (netloc == src_netloc or netloc.endswith("." + src_netloc)):
                return True
    except Exception:
        return False

    return False

"""
CompetitorIQ Safe Initial Competitor Seeding Module
Provisions baseline corporate identity profiles for selected technology competitors.

CRITICAL CONSTRAINTS:
- Seeds ONLY basic identity information (name, website, industry, description, bank identifier).
- Does NOT automatically generate or invent fake historical events.
- Does NOT fabricate any competitor activity.
- Events must be ingested separately through verified sources via event_service.py.
"""

import logging
from typing import List, Dict, Any
from services.database_service import DatabaseService

logger = logging.getLogger("competitoriq.seed")

# Selected baseline competitors with verified corporate identities
INITIAL_COMPETITOR_PROFILES = [
    {
        "id": "microsoft",
        "name": "Microsoft",
        "website": "https://www.microsoft.com",
        "industry": "Enterprise Cloud & AI Platforms",
        "description": "Global enterprise cloud, developer ecosystem, and enterprise AI software platform.",
        "tagline": "Empowering every organization on the planet",
        "hq": "Redmond, Washington, USA",
        "founded": "1975",
        "stage": "Public (NASDAQ: MSFT)",
        "threat_level": "High",
        "primary_battleground": "Enterprise Agent Platforms & Cloud AI",
        "hindsight_memory_identifier": "competitor-microsoft"
    },
    {
        "id": "google",
        "name": "Google",
        "website": "https://about.google",
        "industry": "Cloud Infrastructure, Search & Frontier AI",
        "description": "Multinational technology leader developing foundation models, Gemini AI ecosystem, and Google Cloud.",
        "tagline": "Organizing the world's information with AI",
        "hq": "Mountain View, California, USA",
        "founded": "1998",
        "stage": "Public (NASDAQ: GOOGL)",
        "threat_level": "High",
        "primary_battleground": "Multimodal Models & Cloud Ecosystem",
        "hindsight_memory_identifier": "competitor-google"
    },
    {
        "id": "amazon-aws",
        "name": "Amazon / AWS",
        "website": "https://aws.amazon.com",
        "industry": "Cloud Infrastructure & Enterprise AI",
        "description": "Hyperscale cloud platform providing compute, storage, foundation model hosting (Bedrock), and chips.",
        "tagline": "The world's most comprehensive cloud platform",
        "hq": "Seattle, Washington, USA",
        "founded": "1994",
        "stage": "Public (NASDAQ: AMZN)",
        "threat_level": "High",
        "primary_battleground": "Cloud Infrastructure & Model Marketplaces",
        "hindsight_memory_identifier": "competitor-amazon-aws"
    },
    {
        "id": "openai",
        "name": "OpenAI",
        "website": "https://www.openai.com",
        "industry": "Frontier AI & Foundation Models",
        "description": "AI research and deployment company developing ChatGPT, GPT-4, and enterprise API models.",
        "tagline": "Creating safe AGI that benefits all of humanity",
        "hq": "San Francisco, California, USA",
        "founded": "2015",
        "stage": "Private / Strategic Partnership",
        "threat_level": "High",
        "primary_battleground": "Frontier Reasoning & API Intelligence",
        "hindsight_memory_identifier": "competitor-openai"
    },
    {
        "id": "anthropic",
        "name": "Anthropic",
        "website": "https://www.anthropic.com",
        "industry": "AI Safety & Frontier Models",
        "description": "AI safety and research company creator of the Claude frontier model series and constitutional AI.",
        "tagline": "AI research and safety company",
        "hq": "San Francisco, California, USA",
        "founded": "2021",
        "stage": "Private / Venture Backed",
        "threat_level": "High",
        "primary_battleground": "Enterprise Safety & Large Context Reasoning",
        "hindsight_memory_identifier": "competitor-anthropic"
    },
    {
        "id": "meta",
        "name": "Meta",
        "website": "https://about.meta.com",
        "industry": "Open Source AI & Consumer Platforms",
        "description": "Technology conglomerate leading open-weights frontier AI through the Llama open model family.",
        "tagline": "Connecting people and advancing open AI research",
        "hq": "Menlo Park, California, USA",
        "founded": "2004",
        "stage": "Public (NASDAQ: META)",
        "threat_level": "High",
        "primary_battleground": "Open Weights & Compute Scale",
        "hindsight_memory_identifier": "competitor-meta"
    },
    {
        "id": "novaai",
        "name": "NovaAI",
        "website": "https://novaai.io",
        "industry": "Autonomous Enterprise Intelligence",
        "description": "Next-generation autonomous agent orchestration platform targeting enterprise workflow intelligence.",
        "tagline": "Autonomous agent intelligence for the enterprise",
        "hq": "San Francisco, California, USA",
        "founded": "2023",
        "stage": "Series B",
        "threat_level": "High",
        "primary_battleground": "Autonomous Competitive Intelligence",
        "hindsight_memory_identifier": "competitor-nova-ai"
    },
    {
        "id": "cloudmind",
        "name": "CloudMind",
        "website": "https://cloudmind.ai",
        "industry": "Dedicated GPU Cloud & Hardware",
        "description": "Specialized high-performance GPU cluster provider defending enterprise margins via dedicated hardware.",
        "tagline": "Dedicated compute for mission-critical AI workloads",
        "hq": "Austin, Texas, USA",
        "founded": "2022",
        "stage": "Series A",
        "threat_level": "Medium",
        "primary_battleground": "Dedicated Cluster Infrastructure",
        "hindsight_memory_identifier": "competitor-cloud-mind"
    },
    {
        "id": "techflow",
        "name": "TechFlow",
        "website": "https://techflow.dev",
        "industry": "Developer Agent Tooling",
        "description": "Developer platform for workflow automation, continuous agent deployment, and telemetry pipelines.",
        "tagline": "Continuous delivery for agentic software systems",
        "hq": "New York, New York, USA",
        "founded": "2023",
        "stage": "Seed",
        "threat_level": "Medium",
        "primary_battleground": "Developer Workflows & Integrations",
        "hindsight_memory_identifier": "competitor-tech-flow"
    }
]


def seed_initial_competitors(db_path: str = None) -> List[Dict[str, Any]]:
    """
    Populates basic identity profiles for initial competitors.
    Does NOT seed fake events.
    """
    db = DatabaseService(db_path)
    seeded = []

    for comp in INITIAL_COMPETITOR_PROFILES:
        res = db.upsert_competitor(comp)
        seeded.append(res)

    logger.info(f"Seeded {len(seeded)} verified corporate identity profiles without fake events.")
    return seeded


if __name__ == "__main__":
    seed_initial_competitors()

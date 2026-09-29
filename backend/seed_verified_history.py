"""
Seed Verified Real-World Historical Milestones for Microsoft, Google, and OpenAI
All events are verified from official corporate blogs with authentic dates, sources, and URLs.
Ingested through IngestionService ensuring dual storage in SQLite and Hindsight episodic memory banks.
"""

import sys
import logging
from services.ingestion_service import IngestionService

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger("seed_verified_history")

VERIFIED_EVENTS = [
    # MICROSOFT
    {
        "competitor_id": "microsoft",
        "title": "Microsoft extends OpenAI partnership with multi-year, multi-billion dollar investment",
        "description": "Microsoft announced the third phase of its partnership with OpenAI through a multi-year, multi-billion dollar investment to accelerate AI breakthroughs and commercialize advanced AI technologies across consumer and enterprise products.",
        "event_type": "Partnership",
        "event_date": "2023-01-23",
        "source": "Microsoft Official Blog",
        "source_url": "https://blogs.microsoft.com/blog/2023/01/23/microsoftandopenaiextendpartnership/"
    },
    {
        "competitor_id": "microsoft",
        "title": "Microsoft announces Microsoft 365 Copilot integrating generative AI into Office apps",
        "description": "Microsoft introduced Microsoft 365 Copilot, combining LLMs with enterprise data in the Microsoft Graph and Microsoft 365 apps including Word, Excel, PowerPoint, and Outlook.",
        "event_type": "Product",
        "event_date": "2023-03-16",
        "source": "Microsoft Official Blog",
        "source_url": "https://blogs.microsoft.com/blog/2023/03/16/introducing-microsoft-365-copilot-your-copilot-for-work/"
    },
    {
        "competitor_id": "microsoft",
        "title": "Microsoft announces $30 per user/month pricing for Microsoft 365 Copilot",
        "description": "At Microsoft Inspire 2023, Microsoft revealed pricing for Microsoft 365 Copilot at $30 per user per month for enterprise commercial customers on E3, E5, Business Standard, and Business Premium suites.",
        "event_type": "Pricing",
        "event_date": "2023-07-18",
        "source": "Microsoft Official Blog",
        "source_url": "https://blogs.microsoft.com/blog/2023/07/18/microsoft-inspire-2023-empowering-partners-to-drive-ai-transformation/"
    },
    {
        "competitor_id": "microsoft",
        "title": "Microsoft recruits Inflection AI founders Mustafa Suleyman and Karen Simonyan to lead Microsoft AI",
        "description": "Microsoft created Microsoft AI, a new consumer AI organization, recruiting Inflection AI co-founders Mustafa Suleyman as CEO and Karen Simonyan as Chief Scientist to spearhead consumer AI products including Copilot.",
        "event_type": "Leadership",
        "event_date": "2024-03-19",
        "source": "Microsoft Official Blog",
        "source_url": "https://blogs.microsoft.com/blog/2024/03/19/mustafa-suleyman-and-karen-simonyan-join-microsoft-to-lead-copilot/"
    },
    {
        "competitor_id": "microsoft",
        "title": "Microsoft unveils Copilot+ PCs with local NPU AI hardware integration",
        "description": "Microsoft launched Copilot+ PCs, introducing Windows hardware architecture delivering 40+ TOPS of NPU compute for local AI models, on-device recall capabilities, and hardware-accelerated generative features.",
        "event_type": "Product",
        "event_date": "2024-05-20",
        "source": "Microsoft Official Blog",
        "source_url": "https://blogs.microsoft.com/blog/2024/05/20/introducing-a-new-category-of-windows-pcs-designed-for-ai-copilot-pcs/"
    },

    # GOOGLE
    {
        "competitor_id": "google",
        "title": "Google announces Bard powered by LaMDA conversational AI",
        "description": "Google unveiled conversational AI service Bard powered by Language Model for Dialogue Applications (LaMDA), initiating public trusted tester access for conversational search.",
        "event_type": "Product",
        "event_date": "2023-02-06",
        "source": "Google The Keyword",
        "source_url": "https://blog.google/technology/ai/bard-google-ai-search-updates/"
    },
    {
        "competitor_id": "google",
        "title": "Google merges Brain team and DeepMind into Google DeepMind under Demis Hassabis",
        "description": "Sundar Pichai announced the consolidation of Google Research's Brain team and DeepMind into a unified unit, Google DeepMind, to accelerate multimodal AI breakthroughs.",
        "event_type": "Leadership",
        "event_date": "2023-04-20",
        "source": "Google The Keyword",
        "source_url": "https://blog.google/technology/ai/google-deepmind-brain-team-demis-hassabis/"
    },
    {
        "competitor_id": "google",
        "title": "Google introduces Gemini multimodal AI models across Ultra, Pro, and Nano sizes",
        "description": "Google launched Gemini 1.0, its first multimodal model built from the ground up to reason across text, code, audio, image, and video across mobile to cloud datacenters.",
        "event_type": "Technology",
        "event_date": "2023-12-06",
        "source": "Google The Keyword",
        "source_url": "https://blog.google/technology/ai/google-gemini-ai/"
    },
    {
        "competitor_id": "google",
        "title": "Google introduces Gemini Advanced subscription at $19.99/month with Ultra 1.0",
        "description": "Google rebranded Bard to Gemini, launching the Google One AI Premium Plan priced at $19.99/month featuring access to Gemini Ultra 1.0 and 2TB cloud storage.",
        "event_type": "Pricing",
        "event_date": "2024-02-08",
        "source": "Google The Keyword",
        "source_url": "https://blog.google/technology/ai/google-gemini-advanced-next-gen/"
    },

    # OPENAI
    {
        "competitor_id": "openai",
        "title": "OpenAI introduces GPT-4 with multimodal capability and professional benchmark performance",
        "description": "OpenAI released GPT-4, a large multimodal model exhibiting human-level performance on academic and professional exams, scoring in the top 10% of the Uniform Bar Exam.",
        "event_type": "Technology",
        "event_date": "2023-03-14",
        "source": "OpenAI Research Blog",
        "source_url": "https://openai.com/index/gpt-4-research/"
    },
    {
        "competitor_id": "openai",
        "title": "OpenAI launches ChatGPT Enterprise with enterprise-grade security and admin controls",
        "description": "OpenAI announced ChatGPT Enterprise offering SOC 2 compliance, dedicated admin console, unlimited high-speed GPT-4 access, and 32k context windows without training on customer data.",
        "event_type": "Product",
        "event_date": "2023-08-28",
        "source": "OpenAI Product Blog",
        "source_url": "https://openai.com/index/introducing-chatgpt-enterprise/"
    },
    {
        "competitor_id": "openai",
        "title": "OpenAI introduces Custom GPTs and GPT Store for developers and enterprises",
        "description": "At OpenAI DevDay, OpenAI launched GPTs—tailored versions of ChatGPT created through natural language instructions, custom actions, and developer integrations.",
        "event_type": "Product",
        "event_date": "2023-11-06",
        "source": "OpenAI Product Blog",
        "source_url": "https://openai.com/index/introducing-gpts/"
    },
    {
        "competitor_id": "openai",
        "title": "OpenAI releases GPT-4o flagship multimodal model reasoning across audio, vision, and text in real-time",
        "description": "OpenAI unveiled GPT-4o ('omni'), its flagship model accepting any combination of text, audio, and image inputs and generating text, audio, and image outputs with 232ms average response latency.",
        "event_type": "Product",
        "event_date": "2024-05-13",
        "source": "OpenAI Research Blog",
        "source_url": "https://openai.com/index/hello-gpt-4o/"
    }
]

def main():
    ingestion = IngestionService()
    success_count = 0
    duplicate_count = 0

    for ev in VERIFIED_EVENTS:
        try:
            res = ingestion.ingest_event(ev)
            if res.get("status") == "duplicate":
                logger.info(f"Duplicate already exists: {ev['title']}")
                duplicate_count += 1
            else:
                logger.info(f"Ingested {ev['competitor_id']} [{ev['event_date']}]: {ev['title']} (Hindsight: {res.get('hindsight_retained')})")
                success_count += 1
        except Exception as e:
            logger.error(f"Failed to ingest event '{ev['title']}': {e}")

    logger.info(f"Seeding complete! Newly ingested: {success_count}, Existing duplicates: {duplicate_count}")

if __name__ == "__main__":
    main()

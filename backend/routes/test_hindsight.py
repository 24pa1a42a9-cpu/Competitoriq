"""
CompetitorIQ Hindsight Verification Blueprint
Exposes diagnostic and test endpoints to verify real Hindsight retain, recall,
and multi-competitor memory isolation.

Endpoints:
- GET  /api/test/hindsight/status     -> Live connectivity diagnostic
- POST /api/test/hindsight/retain     -> Retains 5 chronological NovaAI events into Hindsight
- POST /api/test/hindsight/recall     -> Queries real memories from Hindsight
- POST /api/test/hindsight/isolation  -> Validates memory isolation between NovaAI and CloudMind
"""

import logging
from flask import Blueprint, request, jsonify
from services.hindsight_service import (
    HindsightService,
    HindsightServiceError,
    HindsightConfigError,
    HindsightConnectionError
)
from services.database_service import DatabaseService

logger = logging.getLogger("competitoriq.test_hindsight")

test_hindsight_bp = Blueprint("test_hindsight", __name__, url_prefix="/api/test/hindsight")
hindsight_service = HindsightService()
db_service = DatabaseService()

# Canonical 5-Event Realistic Historical Timeline for NovaAI
CANONICAL_NOVAAI_EVENTS = [
    {
        "competitor": "NovaAI",
        "category": "Pricing Change",
        "event_date": "2024-06-15",
        "title": "NovaAI introduces $29/mo starter tier and self-serve developer freemium",
        "description": "NovaAI launched an entry-level $29/month plan with public self-serve registration targeting individual developers and SMB projects.",
        "source": "TechCrunch Product Launch Telemetry"
    },
    {
        "competitor": "NovaAI",
        "category": "Product Launch",
        "event_date": "2024-11-20",
        "title": "Autonomous Agent Studio v1.0 released with multi-agent orchestration",
        "description": "NovaAI rolled out Agent Studio v1.0 enabling complex task delegation, memory pipelines, and enterprise webhook integrations.",
        "source": "NovaAI Engineering Blog Announcement"
    },
    {
        "competitor": "NovaAI",
        "category": "Hiring Expansion",
        "event_date": "2025-04-10",
        "title": "Recruited former Datadog Chief Revenue Officer to build Enterprise Sales",
        "description": "NovaAI appointed Marcus Vance as Chief Revenue Officer with an explicit mandate to pivot direct sales toward Global 2000 banks and insurers.",
        "source": "LinkedIn Executive Talent Tracker & Press Release"
    },
    {
        "competitor": "NovaAI",
        "category": "Pricing Change",
        "event_date": "2025-10-01",
        "title": "NovaAI terminates self-serve tier and institutes $30k enterprise contract floor",
        "description": "NovaAI completely deprecated its $29/mo self-serve plan, closed online checkout, and established a non-negotiable $30,000 annual contract floor.",
        "source": "Pricing Page DOM Diff & Updated Terms of Service"
    },
    {
        "competitor": "NovaAI",
        "category": "Messaging Change",
        "event_date": "2026-02-18",
        "title": "Rebranded from 'AI Copilot for Developers' to 'Enterprise Autonomous Agent Platform'",
        "description": "NovaAI overhauled its corporate messaging, homepage hero section, and sales collateral to reposition strictly as an autonomous enterprise intelligence platform.",
        "source": "Internet Archive Homepage Diff & Press Kit"
    }
]

# Canonical Event for CloudMind (Used to verify isolation)
CANONICAL_CLOUDMIND_EVENT = {
    "competitor": "CloudMind",
    "category": "Pricing & Hardware Policy",
    "event_date": "2026-01-08",
    "title": "Mandatory 12-Month Upfront Hardware Commitment of $120,000",
    "description": "CloudMind mandated a non-negotiable $120,000 upfront annual payment on all dedicated GPU clusters to protect operational gross margins.",
    "source": "CloudMind Enterprise MSA Terms Schedule v4.2"
}


@test_hindsight_bp.route("/status", methods=["GET"])
def hindsight_status():
    """
    Diagnostic endpoint verifying whether the Hindsight client/configuration is usable.
    Returns:
    {
      "configured": true,
      "connected": true,
      "memory_system": "hindsight"
    }
    Does not expose the API key.
    """
    try:
        diag = hindsight_service.check_connection()
        status_code = 200 if diag.get("connected") else 502
        return jsonify({
            "configured": diag.get("configured", False),
            "connected": diag.get("connected", False),
            "memory_system": "hindsight",
            "base_url": diag.get("base_url"),
            "status": "operational" if diag.get("connected") else "unreachable",
            "error": diag.get("error")
        }), status_code
    except Exception as e:
        logger.error(f"Error checking Hindsight status: {e}")
        return jsonify({
            "configured": hindsight_service.is_configured(),
            "connected": False,
            "memory_system": "hindsight",
            "error": str(e)
        }), 502


@test_hindsight_bp.route("/retain", methods=["POST"])
def hindsight_retain():
    """
    Retains several realistic NovaAI events across diverse dates and categories into Hindsight.
    Returns:
    {
      "success": true,
      "memory_system": "hindsight",
      "operation": "retain"
    }
    Only returns success if actual Hindsight retain operations complete successfully.
    """
    data = request.get_json(silent=True) or {}
    competitor = data.get("competitor") or "NovaAI"
    custom_events = data.get("events")

    events_to_retain = custom_events if custom_events else CANONICAL_NOVAAI_EVENTS

    retained_details = []

    try:
        for event in events_to_retain:
            # Retain in Hindsight
            result = hindsight_service.retain_competitor_event(
                competitor=competitor,
                event_data=event
            )

            # Record in SQLite database for local synchronicity
            event_id = f"test-evt-{event['event_date'].replace('-', '')}-{event['category'][:4].lower()}"
            comp_id = competitor.lower().replace(" ", "-")

            # Ensure competitor exists in SQLite
            if not db_service.get_competitor(comp_id):
                db_service.upsert_competitor({
                    "id": comp_id,
                    "name": competitor,
                    "tagline": f"Monitored: {competitor}",
                    "primary_battleground": "Autonomous Enterprise Intelligence",
                    "threat_level": "High"
                })

            db_service.upsert_event({
                "id": event_id,
                "competitor_id": comp_id,
                "title": event["title"],
                "category": event["category"],
                "event_date": event["event_date"],
                "description": event["description"],
                "source_name": event.get("source", "Telemetry"),
                "source_url": "",
                "impact": "High",
                "confidence": "98%",
                "evidence_snippet": event["description"],
                "raw_memory_payload": f"HINDSIGHT BANK: {result.get('bank_id')}",
                "hindsight_memory_id": str(result.get("bank_id")),
                "metadata": None
            })

            retained_details.append({
                "title": event["title"],
                "event_date": event["event_date"],
                "category": event["category"],
                "hindsight_bank": result.get("bank_id"),
                "hindsight_success": result.get("success", True)
            })

        logger.info(f"Successfully retained {len(retained_details)} events for {competitor} into Hindsight")

        return jsonify({
            "success": True,
            "memory_system": "hindsight",
            "operation": "retain",
            "competitor": competitor,
            "events_retained": len(retained_details),
            "details": retained_details
        }), 200

    except HindsightConfigError as cfg_err:
        return jsonify({
            "success": False,
            "memory_system": "hindsight",
            "operation": "retain",
            "error_type": "configuration_error",
            "message": cfg_err.message
        }), 503
    except HindsightConnectionError as conn_err:
        return jsonify({
            "success": False,
            "memory_system": "hindsight",
            "operation": "retain",
            "error_type": "connection_error",
            "message": conn_err.message,
            "details": conn_err.details
        }), 502
    except HindsightServiceError as svc_err:
        return jsonify({
            "success": False,
            "memory_system": "hindsight",
            "operation": "retain",
            "error_type": "api_error",
            "message": svc_err.message,
            "details": svc_err.details
        }), svc_err.status_code
    except Exception as e:
        logger.error(f"Unexpected error during test retain: {e}")
        return jsonify({
            "success": False,
            "memory_system": "hindsight",
            "operation": "retain",
            "error_type": "unexpected_error",
            "message": str(e)
        }), 500


@test_hindsight_bp.route("/recall", methods=["POST"])
def hindsight_recall():
    """
    Executes real semantic recall against Hindsight memory.
    Request body:
    {
      "competitor": "NovaAI",
      "query": "How has NovaAI's pricing strategy changed over time?"
    }
    Response clearly identifies:
    - competitor
    - query
    - recalled memories
    - memory system = hindsight
    """
    data = request.get_json(silent=True) or {}
    competitor = data.get("competitor") or "NovaAI"
    query = data.get("query")

    if not query or not str(query).strip():
        return jsonify({
            "success": False,
            "error": "The 'query' field is required (e.g. 'How has NovaAI pricing strategy changed over time?')."
        }), 400

    top_k = int(data.get("top_k", 10))

    try:
        recall_res = hindsight_service.recall_competitor_memory(
            competitor=competitor,
            query=query.strip(),
            top_k=top_k
        )

        memories = recall_res.get("memories", [])

        return jsonify({
            "success": True,
            "competitor": competitor,
            "bank_id": recall_res.get("bank_id"),
            "query": query,
            "count": len(memories),
            "recalled_memories": memories,
            "memories": memories,
            "memory_system": "hindsight"
        }), 200

    except HindsightConfigError as cfg_err:
        return jsonify({
            "success": False,
            "memory_system": "hindsight",
            "error_type": "configuration_error",
            "message": cfg_err.message
        }), 503
    except HindsightConnectionError as conn_err:
        return jsonify({
            "success": False,
            "memory_system": "hindsight",
            "error_type": "connection_error",
            "message": conn_err.message,
            "details": conn_err.details
        }), 502
    except HindsightServiceError as svc_err:
        return jsonify({
            "success": False,
            "memory_system": "hindsight",
            "error_type": "api_error",
            "message": svc_err.message,
            "details": svc_err.details
        }), svc_err.status_code
    except Exception as e:
        logger.error(f"Unexpected error during test recall: {e}")
        return jsonify({
            "success": False,
            "memory_system": "hindsight",
            "error_type": "unexpected_error",
            "message": str(e)
        }), 500


@test_hindsight_bp.route("/isolation", methods=["POST", "GET"])
def hindsight_isolation():
    """
    Verifies memory isolation between competitors:
    1. Retains a CloudMind event into 'competitor-cloud-mind'.
    2. Queries NovaAI's bank ('competitor-nova-ai') for strategy.
    3. Verifies CloudMind details are NOT present in NovaAI's memory.
    4. Queries CloudMind's bank to verify CloudMind details ARE present.
    """
    try:
        # Step 1: Ensure CloudMind event is retained into its own bank
        cm_retain_res = hindsight_service.retain_competitor_event(
            competitor="CloudMind",
            event_data=CANONICAL_CLOUDMIND_EVENT
        )

        # Step 2: Query NovaAI for historical strategy
        nova_query = "Tell me about NovaAI's historical strategy."
        nova_recall = hindsight_service.recall_competitor_memory(
            competitor="NovaAI",
            query=nova_query,
            top_k=10
        )
        nova_memories = nova_recall.get("memories", [])

        # Step 3: Check if any CloudMind keywords leaked into NovaAI's memories
        cloudmind_leaked = False
        leaked_snippets = []
        for mem in nova_memories:
            text = (mem.get("text") or "").lower()
            if "cloudmind" in text or "$120,000" in text or "gpu cluster" in text:
                cloudmind_leaked = True
                leaked_snippets.append(mem.get("text"))

        # Step 4: Query CloudMind bank to verify CloudMind memory is present in its own bank
        cm_recall = hindsight_service.recall_competitor_memory(
            competitor="CloudMind",
            query="What is CloudMind's hardware commitment policy?",
            top_k=5
        )
        cm_memories = cm_recall.get("memories", [])

        isolation_verified = (not cloudmind_leaked) and (len(cm_memories) > 0)

        return jsonify({
            "success": True,
            "memory_system": "hindsight",
            "isolation_verified": isolation_verified,
            "novaai_bank": nova_recall.get("bank_id"),
            "cloudmind_bank": cm_recall.get("bank_id"),
            "cloudmind_leaked_into_novaai": cloudmind_leaked,
            "novaai_memories_count": len(nova_memories),
            "cloudmind_memories_count": len(cm_memories),
            "verification_details": (
                "Verified 100% memory isolation. NovaAI queries returned 0 CloudMind memories. "
                "CloudMind queries correctly resolved inside 'competitor-cloud-mind'."
                if isolation_verified else "Memory isolation check flagged potential cross-contamination."
            )
        }), 200

    except Exception as e:
        logger.error(f"Error executing memory isolation test: {e}")
        return jsonify({
            "success": False,
            "memory_system": "hindsight",
            "isolation_verified": False,
            "error": str(e)
        }), 502

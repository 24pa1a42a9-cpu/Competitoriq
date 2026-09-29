"""
CompetitorIQ Competitors Blueprint
Handles endpoints for monitored competitor entities:
- GET  /api/competitors              -> Lists all tracked competitors with event metrics
- POST /api/competitors              -> Registers a new competitor with isolated Hindsight bank
- GET  /api/competitors/<id>         -> Retrieves profile details for a single competitor
- GET  /api/competitors/<id>/events  -> Retrieves all events for that competitor
- GET  /api/competitors/<id>/timeline-> Retrieves chronological timeline (ordered by event_date)
"""

import re
import logging
from flask import Blueprint, request, jsonify

from services.database_service import DatabaseService
from services.hindsight_service import HindsightService
from services.pattern_service import PatternService
from services.alert_service import AlertService

logger = logging.getLogger("competitoriq.competitors_bp")
competitors_bp = Blueprint("competitors", __name__, url_prefix="/api/competitors")

db_service = DatabaseService()
hindsight_service = HindsightService()
pattern_service = PatternService()
alert_service = AlertService()


@competitors_bp.route("", methods=["GET"])
def list_competitors():
    """Retrieve all tracked competitors with event counts."""
    try:
        comps = db_service.list_competitors()
        return jsonify({
            "status": "success",
            "count": len(comps),
            "competitors": comps,
            "data": comps,
            "message": f"Retrieved {len(comps)} competitors"
        }), 200
    except Exception as e:
        logger.error(f"Error listing competitors: {e}")
        return jsonify({
            "status": "error",
            "message": f"Failed to retrieve competitors: {str(e)}"
        }), 500


@competitors_bp.route("", methods=["POST"])
def create_competitor():
    """
    Register or update a monitored competitor:
    1. Validates competitor identity fields.
    2. Derives unique slug ID and Hindsight memory bank identifier.
    3. Provisions the dedicated Hindsight memory bank.
    4. Persists the profile in SQLite.
    5. Returns 201 Created with competitor entity.
    """
    data = request.get_json(silent=True) or {}
    name = data.get("name")
    if not name or not str(name).strip():
        return jsonify({
            "status": "error",
            "message": "The competitor 'name' field is required."
        }), 400

    name = str(name).strip()
    comp_id = data.get("id") or re.sub(r"[^a-zA-Z0-9]+", "-", name.lower()).strip("-")

    # Compute and provision isolated Hindsight memory bank
    hindsight_bank = data.get("hindsight_memory_identifier") or hindsight_service.get_bank_id_for_competitor(name)

    try:
        hindsight_service.ensure_bank_exists(name, hindsight_bank)
    except Exception as e:
        logger.warning(f"Note during competitor bank provisioning for '{hindsight_bank}': {e}")

    competitor_payload = {
        "id": comp_id,
        "name": name,
        "website": data.get("website", ""),
        "industry": data.get("industry", "Enterprise Technology"),
        "description": data.get("description", f"Monitored competitive intelligence profile for {name}."),
        "tagline": data.get("tagline", f"Tracked competitor: {name}"),
        "hq": data.get("hq", ""),
        "founded": data.get("founded", ""),
        "stage": data.get("stage", "Public / Enterprise"),
        "arr_estimate": data.get("arr_estimate", ""),
        "employee_count": data.get("employee_count", ""),
        "primary_battleground": data.get("primary_battleground", "Autonomous Enterprise Solutions"),
        "threat_level": data.get("threat_level", "Medium"),
        "strategy_summary": data.get("strategy_summary", ""),
        "why_this_matters": data.get("why_this_matters", ""),
        "hindsight_memory_identifier": hindsight_bank
    }

    try:
        saved = db_service.upsert_competitor(competitor_payload)
        return jsonify({
            "status": "success",
            "competitor": saved,
            "data": saved,
            "hindsight_bank": hindsight_bank,
            "message": f"Competitor '{name}' registered successfully with dedicated Hindsight bank '{hindsight_bank}'."
        }), 201
    except Exception as e:
        logger.error(f"Error saving competitor: {e}")
        return jsonify({
            "status": "error",
            "message": f"Failed to save competitor: {str(e)}"
        }), 500


@competitors_bp.route("/<string:competitor_id>", methods=["GET"])
def get_competitor(competitor_id: str):
    """Retrieve details for a single competitor."""
    try:
        competitor = db_service.get_competitor(competitor_id)
        if not competitor:
            return jsonify({
                "status": "error",
                "message": f"Competitor '{competitor_id}' not found."
            }), 404

        return jsonify({
            "status": "success",
            "competitor": competitor,
            "data": competitor,
            "message": "Competitor found"
        }), 200
    except Exception as e:
        logger.error(f"Error getting competitor {competitor_id}: {e}")
        return jsonify({
            "status": "error",
            "message": f"Failed to retrieve competitor: {str(e)}"
        }), 500


@competitors_bp.route("/<string:competitor_id>/events", methods=["GET"])
def get_competitor_events(competitor_id: str):
    """Retrieve all events recorded for a specific competitor."""
    try:
        competitor = db_service.get_competitor(competitor_id)
        if not competitor:
            return jsonify({
                "status": "error",
                "message": f"Competitor '{competitor_id}' not found."
            }), 404

        events = db_service.list_events(competitor_id=competitor["id"], limit=200)
        return jsonify({
            "status": "success",
            "competitor": competitor,
            "count": len(events),
            "events": events,
            "data": events,
            "message": f"Retrieved {len(events)} events for {competitor['name']}"
        }), 200
    except Exception as e:
        logger.error(f"Error getting events for competitor {competitor_id}: {e}")
        return jsonify({
            "status": "error",
            "message": f"Failed to retrieve events: {str(e)}"
        }), 500


@competitors_bp.route("/<string:competitor_id>/timeline", methods=["GET"])
def get_competitor_timeline(competitor_id: str):
    """
    Retrieve chronological timeline of events for a specific competitor.
    Events are returned in ascending chronological sequence.
    """
    try:
        competitor = db_service.get_competitor(competitor_id)
        if not competitor:
            return jsonify({
                "status": "error",
                "message": f"Competitor '{competitor_id}' not found."
            }), 404

        timeline_events = db_service.list_events(
            competitor_id=competitor["id"],
            order_by="asc",
            limit=200
        )

        return jsonify({
            "status": "success",
            "competitor": competitor,
            "count": len(timeline_events),
            "timeline": timeline_events,
            "events": timeline_events,
            "data": timeline_events,
            "message": f"Retrieved chronological timeline with {len(timeline_events)} milestones for {competitor['name']}"
        }), 200
    except Exception as e:
        logger.error(f"Error getting timeline for competitor {competitor_id}: {e}")
        return jsonify({
            "status": "error",
            "message": f"Failed to retrieve timeline: {str(e)}"
        }), 500


@competitors_bp.route("/<string:competitor_id>/patterns", methods=["GET"])
def get_competitor_patterns(competitor_id: str):
    """
    Step 10: Retrieve strategic patterns detected for a specific competitor.
    Synthesizes stored events and Hindsight episodic memories into cross-category vectors.
    """
    try:
        competitor = db_service.get_competitor(competitor_id)
        if not competitor:
            return jsonify({
                "status": "error",
                "message": f"Competitor '{competitor_id}' not found."
            }), 404

        start_date = request.args.get("start_date")
        end_date = request.args.get("end_date")
        top_k = int(request.args.get("top_k", 10))

        patterns_res = pattern_service.get_patterns(
            competitor=competitor["name"],
            start_date=start_date,
            end_date=end_date,
            top_k=top_k
        )

        return jsonify({
            "status": "success",
            "competitor": competitor,
            "patterns": patterns_res.get("patterns", []),
            "memory_used": patterns_res.get("memory_used", {}),
            "limitations": patterns_res.get("limitations", []),
            "generated_at": patterns_res.get("generated_at")
        }), 200

    except Exception as e:
        logger.error(f"Error getting patterns for competitor {competitor_id}: {e}")
        return jsonify({
            "status": "error",
            "message": f"Failed to detect strategic patterns: {str(e)}"
        }), 500


@competitors_bp.route("/<string:competitor_id>/changes", methods=["GET"])
def get_competitor_changes(competitor_id: str):
    """
    Step 11: "What Changed?" Endpoint
    Compares the competitor's previous checkpoint against newly ingested events.
    Supports ?since=YYYY-MM-DD and ?until=YYYY-MM-DD.
    """
    try:
        competitor = db_service.get_competitor(competitor_id)
        if not competitor:
            return jsonify({
                "status": "error",
                "message": f"Competitor '{competitor_id}' not found."
            }), 404

        since = request.args.get("since")
        until = request.args.get("until")

        changes_res = alert_service.get_changes(
            competitor=competitor["name"],
            since=since,
            until=until
        )

        return jsonify({
            "status": "success",
            "competitor": changes_res["competitor"],
            "competitor_id": changes_res["competitor_id"],
            "since": changes_res["since"],
            "until": changes_res["until"],
            "new_events": changes_res["new_events"],
            "event_count": changes_res["event_count"],
            "by_category": changes_res["by_category"],
            "last_checkpoint": changes_res["last_checkpoint"]
        }), 200

    except Exception as e:
        logger.error(f"Error getting changes for competitor {competitor_id}: {e}")
        return jsonify({
            "status": "error",
            "message": f"Failed to retrieve competitor changes: {str(e)}"
        }), 500

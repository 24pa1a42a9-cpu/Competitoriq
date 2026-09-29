"""
CompetitorIQ Verified Intelligence Ingestion API Routes
Provides endpoints for:
- POST /api/ingestion/events (Single verified source-backed event ingestion)
- POST /api/ingestion/events/bulk (Independent batch ingestion with failure isolation)
- GET /api/ingestion/status (Operational status, retention health, database metrics)
- GET /api/ingestion/sources (Official company source registry discovery)
"""

import logging
from flask import Blueprint, request, jsonify

from services.ingestion_service import IngestionService, IngestionValidationError
from services.hindsight_service import HindsightServiceError, HindsightConfigError, HindsightConnectionError
from config.sources import list_all_registered_sources, get_sources_for_competitor

logger = logging.getLogger("competitoriq.routes.ingestion")

ingestion_bp = Blueprint("ingestion", __name__, url_prefix="/api/ingestion")
ingestion_service = IngestionService()


@ingestion_bp.route("/events", methods=["POST"])
def ingest_event():
    """
    Ingest a single verified, source-backed competitor intelligence event.
    Stores in SQLite and retains into isolated Hindsight memory.
    Rejects duplicates and enforces mandatory source citation.
    """
    payload = request.get_json(silent=True)
    if not payload:
        return jsonify({
            "status": "error",
            "error": "Request body must be a valid JSON object."
        }), 400

    try:
        result = ingestion_service.ingest_event(payload)

        # Return 200 for duplicate, 201 for freshly created event
        status_code = 200 if result.get("status") == "duplicate" else 201
        return jsonify(result), status_code

    except IngestionValidationError as err:
        return jsonify({
            "status": "error",
            "error_type": "validation_error",
            "field": err.field,
            "message": err.message
        }), 400

    except (HindsightServiceError, HindsightConfigError, HindsightConnectionError) as herr:
        logger.error(f"Hindsight retention failed during ingestion: {herr}")
        return jsonify({
            "status": "error",
            "error_type": "hindsight_error",
            "message": herr.message,
            "hindsight_status": "failed"
        }), 502

    except Exception as err:
        logger.error(f"Unexpected error in POST /api/ingestion/events: {err}", exc_info=True)
        return jsonify({
            "status": "error",
            "error_type": "internal_error",
            "message": str(err)
        }), 500


@ingestion_bp.route("/events/bulk", methods=["POST"])
def ingest_events_bulk():
    """
    Bulk ingestion endpoint.
    Processes a list of events independently. One invalid event does not destroy the batch.
    """
    payload = request.get_json(silent=True)
    if not payload or not isinstance(payload, dict):
        return jsonify({
            "status": "error",
            "error": "Request body must be a JSON object containing an 'events' array."
        }), 400

    events_list = payload.get("events")
    if not isinstance(events_list, list):
        return jsonify({
            "status": "error",
            "error": "The 'events' field must be an array of event objects."
        }), 400

    try:
        summary = ingestion_service.ingest_bulk_events(events_list)
        return jsonify(summary), 200

    except Exception as err:
        logger.error(f"Unexpected error in POST /api/ingestion/events/bulk: {err}", exc_info=True)
        return jsonify({
            "status": "error",
            "error_type": "internal_error",
            "message": str(err)
        }), 500


@ingestion_bp.route("/status", methods=["GET"])
def get_ingestion_status():
    """
    Retrieve operational health and status of the ingestion subsystem:
    - SQLite database connection & total events/competitors
    - Hindsight connection & memory retention count
    - Duplicate & pending metrics
    - Official source registry metadata
    (No secrets or API keys are exposed)
    """
    try:
        status_data = ingestion_service.get_ingestion_status()
        return jsonify(status_data), 200
    except Exception as err:
        logger.error(f"Error retrieving ingestion status: {err}", exc_info=True)
        return jsonify({
            "status": "error",
            "message": str(err)
        }), 500


@ingestion_bp.route("/sources", methods=["GET"])
def get_sources():
    """
    Retrieve official registered sources for competitors.
    Optionally filter by ?competitor=<name_or_id>.
    """
    competitor_param = request.args.get("competitor")
    if competitor_param:
        sources = get_sources_for_competitor(competitor_param)
        if not sources:
            return jsonify({
                "status": "not_found",
                "message": f"No registered sources configured for competitor '{competitor_param}'."
            }), 404
        return jsonify({
            "status": "success",
            "competitor": competitor_param,
            "sources": sources
        }), 200

    all_sources = list_all_registered_sources()
    return jsonify({
        "status": "success",
        "count": len(all_sources),
        "sources": all_sources
    }), 200

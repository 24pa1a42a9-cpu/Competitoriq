"""
CompetitorIQ Events Blueprint
Handles endpoints for competitor activity events:
- POST   /api/events         -> Ingests new event (SQLite + Hindsight RETAIN)
- GET    /api/events         -> Queries events with filtering (competitor, type, date range, search)
- GET    /api/events/<id>    -> Retrieves details for a specific event
- DELETE /api/events/<id>    -> Deletes event from SQLite with clear Hindsight status note
- POST   /api/events/retain  -> Backward-compatible alias for ingestion
"""

import logging
from flask import Blueprint, request, jsonify

from services.event_service import EventService, EventValidationError
from services.hindsight_service import (
    HindsightServiceError,
    HindsightConfigError,
    HindsightConnectionError
)

logger = logging.getLogger("competitoriq.events_bp")
events_bp = Blueprint("events", __name__, url_prefix="/api/events")
event_service = EventService()


@events_bp.route("", methods=["POST"])
@events_bp.route("/retain", methods=["POST"])
def ingest_event():
    """
    Primary event ingestion endpoint:
    1. Validates competitor and event schema (mandatory source).
    2. Formats structured memory block.
    3. RETAINS into Hindsight's isolated competitor bank.
    4. Persists in SQLite relational table.
    5. Returns event payload and Hindsight verification.
    """
    data = request.get_json(silent=True) or {}

    try:
        result = event_service.create_competitor_event(data)
        event_obj = result["event"]
        return jsonify({
            "status": "success",
            "message": "Competitor event retained in Hindsight and recorded in database",
            "event": event_obj,
            "hindsight_status": result["hindsight_status"],
            "hindsight": result["hindsight"],
            "competitor": result["competitor"],
            "data": {
                "event_id": event_obj.get("id"),
                "competitor": result["competitor"].get("name"),
                "competitor_id": event_obj.get("competitor_id"),
                "hindsight": result["hindsight"],
                "stored_event": event_obj
            }
        }), 201

    except EventValidationError as val_err:
        return jsonify({
            "status": "error",
            "error_type": "validation_error",
            "field": val_err.field,
            "message": val_err.message
        }), 400

    except HindsightConfigError as cfg_err:
        return jsonify({
            "status": "error",
            "error_type": "hindsight_config_error",
            "message": cfg_err.message
        }), 503

    except HindsightConnectionError as conn_err:
        return jsonify({
            "status": "error",
            "error_type": "hindsight_connection_error",
            "message": conn_err.message,
            "details": conn_err.details
        }), 502

    except HindsightServiceError as svc_err:
        return jsonify({
            "status": "error",
            "error_type": "hindsight_service_error",
            "message": svc_err.message,
            "details": svc_err.details
        }), svc_err.status_code

    except Exception as e:
        logger.error(f"Unexpected error ingesting event: {e}")
        return jsonify({
            "status": "error",
            "error_type": "unexpected_error",
            "message": f"Failed to ingest competitor event: {str(e)}"
        }), 500


@events_bp.route("", methods=["GET"])
def list_events():
    """
    Retrieve competitor events with multi-dimensional filtering:
    - competitor / competitor_id
    - event_type / category
    - start_date / date_from (YYYY-MM-DD)
    - end_date / date_to (YYYY-MM-DD)
    - search (keyword in title, description, or competitor)
    - order_by ('desc' or 'asc')
    - limit
    """
    competitor = request.args.get("competitor") or request.args.get("competitor_id") or request.args.get("competitorId")
    event_type = request.args.get("event_type") or request.args.get("type") or request.args.get("category")
    start_date = request.args.get("start_date") or request.args.get("date_from") or request.args.get("from")
    end_date = request.args.get("end_date") or request.args.get("date_to") or request.args.get("to")
    search = request.args.get("search") or request.args.get("q")
    order_by = request.args.get("order_by", "desc")
    limit = int(request.args.get("limit", 100))

    try:
        events = event_service.get_competitor_events(
            competitor_id=competitor,
            event_type=event_type,
            start_date=start_date,
            end_date=end_date,
            search=search,
            order_by=order_by,
            limit=limit
        )
        return jsonify({
            "status": "success",
            "count": len(events),
            "events": events,
            "data": events,
            "message": f"Retrieved {len(events)} events"
        }), 200

    except Exception as e:
        logger.error(f"Error listing events: {e}")
        return jsonify({
            "status": "error",
            "message": f"Failed to retrieve events: {str(e)}"
        }), 500


@events_bp.route("/<string:event_id>", methods=["GET"])
def get_event(event_id: str):
    """Retrieve details for a specific event by ID."""
    try:
        event = event_service.get_event_by_id(event_id)
        if not event:
            return jsonify({
                "status": "error",
                "message": f"Event '{event_id}' not found."
            }), 404

        return jsonify({
            "status": "success",
            "event": event,
            "data": event,
            "message": "Event retrieved successfully"
        }), 200

    except Exception as e:
        logger.error(f"Error getting event {event_id}: {e}")
        return jsonify({
            "status": "error",
            "message": f"Failed to get event: {str(e)}"
        }), 500


@events_bp.route("/<string:event_id>", methods=["DELETE"])
def delete_event(event_id: str):
    """
    Delete an event from SQLite application database.
    Documents that SQLite deletion and Hindsight memory retention are separate concerns.
    """
    try:
        res = event_service.delete_event(event_id)
        if not res["found"]:
            return jsonify({
                "status": "error",
                "message": f"Event '{event_id}' not found."
            }), 404

        return jsonify({
            "status": "success",
            "deleted_id": event_id,
            "hindsight_note": res["hindsight_note"],
            "message": f"Event '{event_id}' deleted from database."
        }), 200

    except Exception as e:
        logger.error(f"Error deleting event {event_id}: {e}")
        return jsonify({
            "status": "error",
            "message": f"Failed to delete event: {str(e)}"
        }), 500

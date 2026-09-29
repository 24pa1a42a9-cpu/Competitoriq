"""
CompetitorIQ Strategic Alerts API Blueprint (Step 11)
Endpoints for proactive intelligence notifications, "What Changed?" analysis,
and alert state management (new, read, dismissed).
"""

import logging
from flask import Blueprint, request, jsonify

from services.alert_service import AlertService
from services.analyst_service import AnalystValidationError, UnknownCompetitorError
from services.hindsight_service import HindsightServiceError, HindsightConfigError
from services.llm_service import GroqServiceError, GroqConfigError

logger = logging.getLogger("competitoriq.routes.alerts")

alerts_bp = Blueprint("alerts", __name__, url_prefix="/api/alerts")
alert_service = AlertService()


@alerts_bp.route("", methods=["GET"])
def list_alerts():
    """
    Retrieve real strategic competitive alerts.
    Supports query parameter filters:
    - ?competitor_id= (or ?competitor=)
    - ?status= (new | read | dismissed)
    - ?event_type= (Product | Pricing | Leadership | etc.)
    - ?limit= (default 50)
    """
    competitor_id = request.args.get("competitor_id") or request.args.get("competitor")
    status = request.args.get("status")
    event_type = request.args.get("event_type")
    limit = int(request.args.get("limit", 50))

    try:
        alerts = alert_service.list_alerts(
            competitor_id=competitor_id,
            status=status,
            event_type=event_type,
            limit=limit
        )

        # Count unread
        unread_count = len([a for a in alerts if a.get("status") == "new"])

        return jsonify({
            "status": "success",
            "count": len(alerts),
            "unread_count": unread_count,
            "alerts": alerts,
            "data": alerts
        }), 200

    except Exception as e:
        logger.error(f"Error listing alerts: {e}", exc_info=True)
        return jsonify({
            "status": "error",
            "message": f"Failed to retrieve alerts: {str(e)}"
        }), 500


@alerts_bp.route("/<string:alert_id>", methods=["GET"])
def get_alert_detail(alert_id: str):
    """Retrieve details for a single alert."""
    try:
        alert = alert_service.db.get_alert(alert_id)
        if not alert:
            return jsonify({
                "status": "error",
                "message": f"Alert '{alert_id}' not found."
            }), 404
        return jsonify({
            "status": "success",
            "alert": alert
        }), 200
    except Exception as e:
        logger.error(f"Error getting alert {alert_id}: {e}")
        return jsonify({
            "status": "error",
            "message": str(e)
        }), 500


@alerts_bp.route("/generate", methods=["POST"])
def generate_alerts():
    """
    Proactively evaluates new competitor activity since last checkpoint:
    1. Finds events since last checkpoint.
    2. Recalls related historical Hindsight episodic context.
    3. Synthesizes strategic significance with Groq.
    4. Persists verified alerts with duplicate protection.
    5. Updates checkpoint timestamp.
    """
    data = request.get_json(silent=True) or {}
    competitor = data.get("competitor") or data.get("competitor_id") or data.get("competitor_name")
    since = data.get("since")

    if not competitor:
        return jsonify({
            "status": "error",
            "message": "The 'competitor' field is required."
        }), 400

    try:
        result = alert_service.generate_alerts(
            competitor=competitor,
            since=since
        )
        return jsonify(result), 200

    except UnknownCompetitorError as err:
        return jsonify({
            "status": "error",
            "error_type": "unknown_competitor",
            "message": err.message
        }), 404

    except GroqConfigError as g_cfg_err:
        return jsonify({
            "status": "error",
            "error_type": "groq_not_configured",
            "message": g_cfg_err.message
        }), 503

    except GroqServiceError as g_svc_err:
        return jsonify({
            "status": "error",
            "error_type": "groq_service_error",
            "message": g_svc_err.message
        }), g_svc_err.status_code

    except Exception as err:
        logger.error(f"Unexpected error generating alerts: {err}", exc_info=True)
        return jsonify({
            "status": "error",
            "message": str(err)
        }), 500


@alerts_bp.route("/<string:alert_id>/read", methods=["PATCH", "POST"])
def mark_alert_read(alert_id: str):
    """Mark an alert as 'read'."""
    try:
        updated = alert_service.mark_read(alert_id)
        if not updated:
            return jsonify({
                "status": "error",
                "message": f"Alert '{alert_id}' not found."
            }), 404
        return jsonify({
            "status": "success",
            "message": f"Alert '{alert_id}' marked as read.",
            "alert": updated
        }), 200
    except Exception as e:
        logger.error(f"Error marking alert {alert_id} as read: {e}")
        return jsonify({
            "status": "error",
            "message": str(e)
        }), 500


@alerts_bp.route("/<string:alert_id>/dismiss", methods=["PATCH", "POST"])
def mark_alert_dismissed(alert_id: str):
    """Mark an alert as 'dismissed' without deleting evidence."""
    try:
        updated = alert_service.mark_dismissed(alert_id)
        if not updated:
            return jsonify({
                "status": "error",
                "message": f"Alert '{alert_id}' not found."
            }), 404
        return jsonify({
            "status": "success",
            "message": f"Alert '{alert_id}' dismissed.",
            "alert": updated
        }), 200
    except Exception as e:
        logger.error(f"Error dismissing alert {alert_id}: {e}")
        return jsonify({
            "status": "error",
            "message": str(e)
        }), 500

"""
CompetitorIQ Executive Intelligence Brief Routes (Step 12)
Endpoint:
POST /api/reports/competitor
GET  /api/reports/competitor/<id>
"""

import logging
from flask import Blueprint, request, jsonify

from services.report_service import ReportService
from services.analyst_service import AnalystValidationError, UnknownCompetitorError

logger = logging.getLogger("competitoriq.routes.reports")
reports_bp = Blueprint("reports", __name__, url_prefix="/api/reports")

# Initialize service
report_service = ReportService()


@reports_bp.route("/competitor", methods=["POST"])
def generate_competitor_report():
    """
    Generate an Executive Intelligence Briefing for a competitor.
    Request JSON:
    {
        "competitor": "Microsoft",
        "time_range": "all" | "last_30_days" | "last_90_days" | "last_180_days"
    }
    """
    try:
        data = request.get_json(silent=True) or {}
        competitor = data.get("competitor")
        time_range = data.get("time_range", "all")

        if not competitor:
            return jsonify({
                "status": "error",
                "error": "The 'competitor' parameter is required.",
                "code": "MISSING_COMPETITOR"
            }), 400

        report = report_service.generate_brief(
            competitor=competitor,
            time_range=time_range
        )

        return jsonify({
            "status": "success",
            "report": report
        }), 200

    except AnalystValidationError as e:
        logger.warning(f"Validation error in report generation: {e}")
        return jsonify({
            "status": "error",
            "error": str(e),
            "field": getattr(e, "field", None),
            "code": "VALIDATION_ERROR"
        }), 400

    except UnknownCompetitorError as e:
        logger.warning(f"Competitor not found: {e}")
        return jsonify({
            "status": "error",
            "error": str(e),
            "code": "COMPETITOR_NOT_FOUND"
        }), 404

    except Exception as e:
        logger.error(f"Unexpected error generating executive brief: {e}", exc_info=True)
        return jsonify({
            "status": "error",
            "error": "An internal error occurred while synthesizing the executive intelligence brief.",
            "code": "INTERNAL_SERVER_ERROR"
        }), 500


@reports_bp.route("/competitor/<competitor_id>", methods=["GET"])
def get_competitor_report(competitor_id: str):
    """
    Convenience GET endpoint for generating or retrieving an Executive Brief.
    Query params: ?time_range=all
    """
    try:
        time_range = request.args.get("time_range", "all")
        report = report_service.generate_brief(
            competitor=competitor_id,
            time_range=time_range
        )
        return jsonify({
            "status": "success",
            "report": report
        }), 200

    except UnknownCompetitorError as e:
        return jsonify({
            "status": "error",
            "error": str(e),
            "code": "COMPETITOR_NOT_FOUND"
        }), 404

    except AnalystValidationError as e:
        return jsonify({
            "status": "error",
            "error": str(e),
            "code": "VALIDATION_ERROR"
        }), 400

    except Exception as e:
        logger.error(f"Error in GET executive report: {e}", exc_info=True)
        return jsonify({
            "status": "error",
            "error": "Failed to generate executive report.",
            "code": "INTERNAL_SERVER_ERROR"
        }), 500

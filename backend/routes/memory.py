"""
CompetitorIQ Memory Blueprint
Handles endpoints for querying Hindsight memory banks:
- POST /api/memory/recall   Retrieve isolated historical memories for a competitor
- GET  /api/memory/status   Check Hindsight service connectivity and bank status
"""

from flask import Blueprint, request
from services.hindsight_service import (
    HindsightService,
    HindsightServiceError,
    HindsightConfigError,
    HindsightConnectionError
)
from utils.helpers import success_response, error_response

memory_bp = Blueprint("memory", __name__, url_prefix="/api/memory")
hindsight_service = HindsightService()


@memory_bp.route("/status", methods=["GET"])
def memory_status():
    """Retrieve Hindsight memory engine configuration and status."""
    return success_response(
        data=hindsight_service.get_status(),
        message="Hindsight status retrieved"
    )


@memory_bp.route("/recall", methods=["POST"])
def recall_memory():
    """
    Primary memory retrieval endpoint for CompetitorIQ:
    1. Validates competitor and search query.
    2. Directs the query to the competitor's isolated Hindsight bank.
    3. Retrieves actual memories, metadata, evidence snippets, and relevance scores.
    4. Returns exact Hindsight response without fabrication.
    """
    data = request.get_json() or {}

    # 1. Validation
    competitor = data.get("competitor")
    if not competitor or not str(competitor).strip():
        return error_response(
            message="The 'competitor' field is required (e.g. 'NovaAI').",
            status_code=400
        )

    query = data.get("query")
    if not query or not str(query).strip():
        return error_response(
            message="The 'query' field cannot be empty.",
            status_code=400
        )

    top_k = int(data.get("top_k", 5))

    # 2. Recall from Hindsight Memory Bank
    try:
        recall_result = hindsight_service.recall_competitor_memory(
            competitor=competitor,
            query=query,
            top_k=top_k
        )

        from flask import jsonify
        return jsonify({
            "status": "success",
            "competitor": recall_result["competitor"],
            "bank_id": recall_result["bank_id"],
            "query": recall_result["query"],
            "count": recall_result["count"],
            "memories": recall_result["memories"],
            "memory_source": recall_result["memory_source"],
            "data": recall_result,
            "message": f"Recalled {recall_result['count']} memories from Hindsight bank '{recall_result['bank_id']}'"
        }), 200

    except HindsightConfigError as cfg_err:
        return error_response(
            message=cfg_err.message,
            status_code=cfg_err.status_code
        )
    except HindsightConnectionError as conn_err:
        return error_response(
            message=conn_err.message,
            status_code=conn_err.status_code,
            details=conn_err.details
        )
    except HindsightServiceError as svc_err:
        return error_response(
            message=svc_err.message,
            status_code=svc_err.status_code,
            details=svc_err.details
        )
    except ValueError as val_err:
        return error_response(message=str(val_err), status_code=400)
    except Exception as e:
        return error_response(
            message=f"Unexpected error querying Hindsight: {str(e)}",
            status_code=502
        )

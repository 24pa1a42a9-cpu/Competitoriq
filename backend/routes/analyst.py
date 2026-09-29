"""
CompetitorIQ Strategic AI Analyst API Blueprint
Coordinates Hindsight episodic memory recall with Groq LLM reasoning.

Endpoints:
- POST /api/analyst/analyze: Single-competitor strategic intelligence reasoning
- POST /api/analyst/compare: Multi-competitor cross-company comparison reasoning
- GET /api/analyst/status: Analyst subsystem readiness & configuration status
"""

import logging
from flask import Blueprint, request, jsonify

from services.analyst_service import (
    AnalystService,
    AnalystValidationError,
    UnknownCompetitorError
)
from services.hindsight_comparison_service import HindsightComparisonService
from services.pattern_service import PatternService
from services.hindsight_service import (
    HindsightServiceError,
    HindsightConfigError,
    HindsightConnectionError
)
from services.llm_service import (
    GroqConfigError,
    GroqServiceError,
    LLMServiceError
)

logger = logging.getLogger("competitoriq.routes.analyst")

analyst_bp = Blueprint("analyst", __name__, url_prefix="/api/analyst")
analyst_service = AnalystService()
comparison_service = HindsightComparisonService()
pattern_service = PatternService()


@analyst_bp.route("/status", methods=["GET"])
def analyst_status():
    """
    Check configuration readiness of Hindsight Memory and Groq LLM.
    Does not expose API keys.
    """
    h_status = analyst_service.hindsight.get_status()
    l_status = analyst_service.llm.get_status()

    return jsonify({
        "status": "ok",
        "hindsight": h_status,
        "llm": l_status,
        "ready_for_synthesis": h_status.get("configured", False) and l_status.get("configured", False)
    }), 200


@analyst_bp.route("/analyze", methods=["POST"])
@analyst_bp.route("/query", methods=["POST"])
def analyze_competitor():
    """
    Single-competitor strategic reasoning endpoint:
    User Question
        ↓
    Hindsight RECALL (Isolated memory bank)
        ↓
    Relevant Historical Memories
        ↓
    Groq LLM Reasoning (openai/gpt-oss-120b)
        ↓
    Evidence-backed Competitive Intelligence Response
    """
    data = request.get_json(silent=True) or {}

    competitor = data.get("competitor") or data.get("competitor_id") or data.get("competitor_name")
    question = data.get("question") or data.get("prompt") or data.get("query")
    start_date = data.get("start_date")
    end_date = data.get("end_date")
    top_k = int(data.get("top_k", 10))

    try:
        result = analyst_service.analyze_competitor(
            competitor=competitor,
            question=question,
            start_date=start_date,
            end_date=end_date,
            top_k=top_k
        )
        return jsonify(result), 200

    except AnalystValidationError as err:
        return jsonify({
            "status": "error",
            "error_type": "validation_error",
            "field": err.field,
            "message": err.message
        }), 400

    except UnknownCompetitorError as err:
        return jsonify({
            "status": "error",
            "error_type": "unknown_competitor",
            "message": err.message
        }), 404

    except HindsightConfigError as cfg_err:
        return jsonify({
            "status": "error",
            "error_type": "hindsight_config_error",
            "message": cfg_err.message
        }), 503

    except (HindsightConnectionError, HindsightServiceError) as h_err:
        logger.error(f"Hindsight error during analysis: {h_err}")
        return jsonify({
            "status": "error",
            "error_type": "hindsight_error",
            "message": h_err.message
        }), 502

    except GroqConfigError as g_cfg_err:
        logger.warning(f"Groq not configured: {g_cfg_err.message}")
        return jsonify({
            "status": "error",
            "error_type": "groq_not_configured",
            "message": g_cfg_err.message
        }), 503

    except GroqServiceError as g_svc_err:
        logger.error(f"Groq service error during analysis: {g_svc_err}")
        return jsonify({
            "status": "error",
            "error_type": "groq_service_error",
            "message": g_svc_err.message
        }), g_svc_err.status_code

    except Exception as err:
        logger.error(f"Unexpected error in /api/analyst/analyze: {err}", exc_info=True)
        return jsonify({
            "status": "error",
            "error_type": "internal_error",
            "message": str(err)
        }), 500


@analyst_bp.route("/compare", methods=["POST"])
def compare_competitors():
    """
    Multi-competitor cross-company comparison endpoint:
    For EACH competitor:
    1. Recall dedicated Hindsight memory bank.
    2. Maintain strict memory isolation.
    3. Pass company-specific memories to Groq.
    4. Synthesize company insights, shared patterns, and differences.
    """
    data = request.get_json(silent=True) or {}

    competitors = data.get("competitors")
    question = data.get("question") or data.get("prompt")
    top_k = int(data.get("top_k", 10))

    try:
        result = analyst_service.compare_competitors(
            competitors=competitors,
            question=question,
            top_k=top_k
        )
        return jsonify(result), 200

    except AnalystValidationError as err:
        return jsonify({
            "status": "error",
            "error_type": "validation_error",
            "field": err.field,
            "message": err.message
        }), 400

    except UnknownCompetitorError as err:
        return jsonify({
            "status": "error",
            "error_type": "unknown_competitor",
            "message": err.message
        }), 404

    except HindsightConfigError as cfg_err:
        return jsonify({
            "status": "error",
            "error_type": "hindsight_config_error",
            "message": cfg_err.message
        }), 503

    except (HindsightConnectionError, HindsightServiceError) as h_err:
        logger.error(f"Hindsight error during comparison: {h_err}")
        return jsonify({
            "status": "error",
            "error_type": "hindsight_error",
            "message": h_err.message
        }), 502

    except GroqConfigError as g_cfg_err:
        logger.warning(f"Groq not configured: {g_cfg_err.message}")
        return jsonify({
            "status": "error",
            "error_type": "groq_not_configured",
            "message": g_cfg_err.message
        }), 503

    except GroqServiceError as g_svc_err:
        logger.error(f"Groq service error during comparison: {g_svc_err}")
        return jsonify({
            "status": "error",
            "error_type": "groq_service_error",
            "message": g_svc_err.message
        }), g_svc_err.status_code

    except Exception as err:
        logger.error(f"Unexpected error in /api/analyst/compare: {err}", exc_info=True)
        return jsonify({
            "status": "error",
            "error_type": "internal_error",
            "message": str(err)
        }), 500


@analyst_bp.route("/before-after", methods=["POST"])
@analyst_bp.route("/benchmark", methods=["POST", "GET"])
def before_after_analysis():
    """
    Step 9: Before vs After Hindsight Demonstration Endpoint
    Compares baseline limited context reasoning against Hindsight-powered temporal reasoning.
    Flow:
      BEFORE: Baseline observable move, 0 memories recalled, recency bias constraints
      AFTER:  Target competitor Hindsight RECALL -> Historical memory trail -> Groq temporal reasoning
      IMPROVEMENT: Verifiable metrics on memories added, events connected, patterns found
    """
    if request.method == "GET":
        competitor = request.args.get("competitor", "Microsoft")
        question = request.args.get("question", f"How has {competitor}'s AI strategy evolved?")
        start_date = request.args.get("start_date")
        end_date = request.args.get("end_date")
        top_k = int(request.args.get("top_k", 10))
    else:
        data = request.get_json(silent=True) or {}
        competitor = data.get("competitor") or data.get("competitor_id") or data.get("competitor_name")
        question = data.get("question") or data.get("prompt") or data.get("query")
        start_date = data.get("start_date")
        end_date = data.get("end_date")
        top_k = int(data.get("top_k", 10))

    try:
        result = comparison_service.compare_before_after(
            competitor=competitor,
            question=question,
            start_date=start_date,
            end_date=end_date,
            top_k=top_k
        )
        return jsonify(result), 200

    except AnalystValidationError as err:
        return jsonify({
            "status": "error",
            "error_type": "validation_error",
            "field": err.field,
            "message": err.message
        }), 400

    except UnknownCompetitorError as err:
        return jsonify({
            "status": "error",
            "error_type": "unknown_competitor",
            "message": err.message
        }), 404

    except HindsightConfigError as cfg_err:
        return jsonify({
            "status": "error",
            "error_type": "hindsight_config_error",
            "message": cfg_err.message
        }), 503

    except (HindsightConnectionError, HindsightServiceError) as h_err:
        logger.error(f"Hindsight error during before-after: {h_err}")
        return jsonify({
            "status": "error",
            "error_type": "hindsight_error",
            "message": h_err.message
        }), 502

    except GroqConfigError as g_cfg_err:
        logger.warning(f"Groq not configured: {g_cfg_err.message}")
        return jsonify({
            "status": "error",
            "error_type": "groq_not_configured",
            "message": g_cfg_err.message
        }), 503

    except GroqServiceError as g_svc_err:
        logger.error(f"Groq service error during before-after: {g_svc_err}")
        return jsonify({
            "status": "error",
            "error_type": "groq_service_error",
            "message": g_svc_err.message
        }), g_svc_err.status_code

    except Exception as err:
        logger.error(f"Unexpected error in /api/analyst/before-after: {err}", exc_info=True)
        return jsonify({
            "status": "error",
            "error_type": "internal_error",
            "message": str(err)
        }), 500


@analyst_bp.route("/patterns", methods=["POST", "GET"])
def detect_patterns():
    """
    Step 10: Strategic Pattern Detection & Connect the Dots Endpoint
    Identifies meaningful temporal and cross-category patterns across stored
    competitor events and Hindsight episodic memories.
    """
    if request.method == "GET":
        competitor = request.args.get("competitor", "Microsoft")
        start_date = request.args.get("start_date")
        end_date = request.args.get("end_date")
        top_k = int(request.args.get("top_k", 10))
    else:
        data = request.get_json(silent=True) or {}
        competitor = data.get("competitor") or data.get("competitor_id") or data.get("competitor_name")
        start_date = data.get("start_date")
        end_date = data.get("end_date")
        top_k = int(data.get("top_k", 10))

    try:
        result = pattern_service.get_patterns(
            competitor=competitor,
            start_date=start_date,
            end_date=end_date,
            top_k=top_k
        )
        return jsonify(result), 200

    except AnalystValidationError as err:
        return jsonify({
            "status": "error",
            "error_type": "validation_error",
            "field": err.field,
            "message": err.message
        }), 400

    except UnknownCompetitorError as err:
        return jsonify({
            "status": "error",
            "error_type": "unknown_competitor",
            "message": err.message
        }), 404

    except HindsightConfigError as cfg_err:
        return jsonify({
            "status": "error",
            "error_type": "hindsight_config_error",
            "message": cfg_err.message
        }), 503

    except (HindsightConnectionError, HindsightServiceError) as h_err:
        logger.error(f"Hindsight error during pattern detection: {h_err}")
        return jsonify({
            "status": "error",
            "error_type": "hindsight_error",
            "message": h_err.message
        }), 502

    except GroqConfigError as g_cfg_err:
        logger.warning(f"Groq not configured: {g_cfg_err.message}")
        return jsonify({
            "status": "error",
            "error_type": "groq_not_configured",
            "message": g_cfg_err.message
        }), 503

    except GroqServiceError as g_svc_err:
        logger.error(f"Groq service error during pattern detection: {g_svc_err}")
        return jsonify({
            "status": "error",
            "error_type": "groq_service_error",
            "message": g_svc_err.message
        }), g_svc_err.status_code

    except Exception as err:
        logger.error(f"Unexpected error in /api/analyst/patterns: {err}", exc_info=True)
        return jsonify({
            "status": "error",
            "error_type": "internal_error",
            "message": str(err)
        }), 500

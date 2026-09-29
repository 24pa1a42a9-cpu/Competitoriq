"""
CompetitorIQ Flask Application Entry Point
Initializes Flask, sets up CORS for the frontend UI, connects SQLite database,
and registers API route blueprints.
"""

import logging
from flask import Flask, jsonify
from flask_cors import CORS

from config import Config
from models.database import init_db
from routes.competitors import competitors_bp
from routes.events import events_bp
from routes.analyst import analyst_bp
from routes.memory import memory_bp
from routes.test_hindsight import test_hindsight_bp
from routes.ingestion import ingestion_bp
from routes.alerts import alerts_bp
from routes.reports import reports_bp
from services.hindsight_service import HindsightService
from services.llm_service import LLMService

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s"
)
logger = logging.getLogger("competitoriq.app")


def create_app(config_class=Config) -> Flask:
    """Application factory for CompetitorIQ backend."""
    app = Flask(__name__)
    app.config.from_object(config_class)

    # 1. Configure CORS specifically for the Vite frontend development server
    CORS(
        app,
        resources={r"/api/*": {"origins": ["http://localhost:5173", "http://127.0.0.1:5173"]}},
        supports_credentials=True
    )

    # 2. Initialize the SQLite database schema
    init_db(app.config["DB_PATH"])

    # 3. Register route blueprints
    app.register_blueprint(competitors_bp)
    app.register_blueprint(events_bp)
    app.register_blueprint(ingestion_bp)
    app.register_blueprint(analyst_bp)
    app.register_blueprint(memory_bp)
    app.register_blueprint(test_hindsight_bp)
    app.register_blueprint(alerts_bp)
    app.register_blueprint(reports_bp)

    # 4. Extended Health Check Endpoint (Step 13 Hardened)
    hindsight_service = HindsightService()
    llm_service = LLMService()

    @app.route("/api/health", methods=["GET"])
    def health_check():
        """
        Health check endpoint reporting dependency service availability:
        backend, database, hindsight, and groq.
        """
        # Test database connectivity
        db_status = "ok"
        try:
            from models.database import get_db_connection
            with get_db_connection(app.config["DB_PATH"]) as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT 1")
                cursor.fetchone()
        except Exception as e:
            logger.error(f"Database health check failed: {e}")
            db_status = "unavailable"

        # Check Hindsight configuration/availability
        hs_status = "ok" if hindsight_service.is_configured() else "unavailable"

        # Check Groq configuration/availability
        groq_status = "ok" if llm_service.is_configured() else "unavailable"

        overall_status = "ok" if (db_status == "ok" and hs_status == "ok" and groq_status == "ok") else "degraded"

        return jsonify({
            "status": overall_status,
            "backend": "ok",
            "database": db_status,
            "hindsight": hs_status,
            "groq": groq_status,
            "service": "CompetitorIQ backend"
        }), 200

    logger.info("CompetitorIQ backend application created successfully")
    return app


# Application instance
app = create_app()

if __name__ == "__main__":
    logger.info(f"Starting CompetitorIQ Flask server on port {Config.PORT}...")
    app.run(
        host="0.0.0.0",
        port=Config.PORT,
        debug=Config.DEBUG
    )

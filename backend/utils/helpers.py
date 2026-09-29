"""
CompetitorIQ Utility Helpers
Standardized response wrappers and serialization helpers for API endpoints.
"""

from typing import Any, Optional
from flask import jsonify, Response
import sqlite3


def row_to_dict(row: Optional[sqlite3.Row]) -> Optional[dict]:
    """Convert an SQLite Row object to a standard Python dictionary."""
    if row is None:
        return None
    return {key: row[key] for key in row.keys()}


def success_response(
    data: Any = None,
    message: str = "Success",
    status_code: int = 200
) -> tuple[Response, int]:
    """Generate a standard JSON success response."""
    payload = {
        "status": "success",
        "message": message,
        "data": data
    }
    return jsonify(payload), status_code


def error_response(
    message: str = "An error occurred",
    status_code: int = 400,
    details: Any = None
) -> tuple[Response, int]:
    """Generate a standard JSON error response."""
    payload = {
        "status": "error",
        "message": message
    }
    if details is not None:
        payload["details"] = details
    return jsonify(payload), status_code

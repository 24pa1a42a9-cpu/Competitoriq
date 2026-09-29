"""
CompetitorIQ Event Ingestion & Synchronization Service Layer
Coordinates structured event persistence in SQLite with episodic memory retention in Hindsight.

Architecture Flow:
Incoming Event Payload
        ↓
Validation (Competitor, Title, Event Type, Date, Mandatory Source)
        ↓
Format Context-Rich Memory Block (COMPETITOR, EVENT TYPE, DATE, EVENT, SOURCE, SIGNIFICANCE)
        ↓
Hindsight RETAIN (Targeted Competitor Bank)
        ↓
SQLite Ingestion (competitor_events table)
        ↓
Verified Event Return + Hindsight Status Verification
"""

import uuid
import logging
import re
from typing import Dict, Any, List, Optional
from datetime import datetime

from services.database_service import DatabaseService
from services.hindsight_service import (
    HindsightService,
    HindsightServiceError,
    HindsightConfigError,
    HindsightConnectionError
)

logger = logging.getLogger("competitoriq.event_service")

# Supported Canonical Event Types
SUPPORTED_EVENT_TYPES = {
    "product": "Product",
    "pricing": "Pricing",
    "hiring": "Hiring",
    "partnership": "Partnership",
    "acquisition": "Acquisition",
    "messaging": "Messaging",
    "funding": "Funding",
    "leadership": "Leadership",
    "technology": "Technology",
    "market expansion": "Market Expansion",
    "market_expansion": "Market Expansion",
    "other": "Other"
}


class EventValidationError(Exception):
    """Raised when an incoming event payload fails data quality constraints."""
    def __init__(self, message: str, field: Optional[str] = None):
        super().__init__(message)
        self.message = message
        self.field = field


class EventService:
    """
    High-level event lifecycle orchestrator.
    Guarantees dual persistence across structured relational storage and Hindsight episodic memory.
    """

    def __init__(
        self,
        db_service: Optional[DatabaseService] = None,
        hindsight_service: Optional[HindsightService] = None
    ):
        self.db = db_service or DatabaseService()
        self.hindsight = hindsight_service or HindsightService()

    def _normalize_event_type(self, raw_type: Optional[str]) -> str:
        """Map raw input string to standard canonical event type."""
        if not raw_type or not str(raw_type).strip():
            return "Other"
        key = str(raw_type).strip().lower().replace("-", " ")
        return SUPPORTED_EVENT_TYPES.get(key, "Other")

    def _validate_event_payload(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Enforce strict data quality rules on the incoming event:
        Every event must have competitor, date, event type, title, description, and source.
        """
        # 1. Competitor Identification
        competitor = data.get("competitor") or data.get("competitor_name") or data.get("competitor_id")
        if not competitor or not str(competitor).strip():
            raise EventValidationError("The 'competitor' or 'competitor_id' field is required.", field="competitor")

        # 2. Title
        title = data.get("title")
        if not title or not str(title).strip():
            raise EventValidationError("The 'title' field is required and cannot be empty.", field="title")

        # 3. Event Date
        event_date = data.get("event_date") or data.get("date")
        if not event_date or not str(event_date).strip():
            raise EventValidationError("The 'event_date' field is required (YYYY-MM-DD).", field="event_date")

        date_str = str(event_date).strip().split("T")[0]
        try:
            datetime.strptime(date_str, "%Y-%m-%d")
        except ValueError:
            raise EventValidationError(f"Invalid date format '{event_date}'. Must be YYYY-MM-DD.", field="event_date")

        # 4. Event Type
        event_type = self._normalize_event_type(data.get("event_type") or data.get("category"))

        # 5. Description
        description = data.get("description")
        if not description or not str(description).strip():
            raise EventValidationError("The 'description' field is required to establish context.", field="description")

        # 6. Source (Mandatory for factual intelligence integrity)
        source_name = data.get("source_name") or data.get("source")
        if not source_name or not str(source_name).strip():
            raise EventValidationError(
                "A verified 'source_name' or 'source' is strictly required for intelligence integrity.",
                field="source_name"
            )

        # 7. URL Validation (if supplied)
        source_url = data.get("source_url") or ""
        if source_url and not (source_url.startswith("http://") or source_url.startswith("https://")):
            raise EventValidationError(f"Invalid source_url '{source_url}'. Must begin with http:// or https://.", field="source_url")

        return {
            "competitor_raw": str(competitor).strip(),
            "title": str(title).strip(),
            "event_date": date_str,
            "event_type": event_type,
            "description": str(description).strip(),
            "source_name": str(source_name).strip(),
            "source_url": str(source_url).strip(),
            "impact": data.get("impact", "Moderate"),
            "confidence": data.get("confidence", "95%"),
            "significance": data.get("significance", "").strip()
        }

    def _format_memory_representation(
        self,
        competitor_name: str,
        validated: Dict[str, Any]
    ) -> str:
        """
        Creates a structured, context-rich memory block for Hindsight:
        Competitor: ...
        Event Type: ...
        Event Date: ...
        Event: ...
        Details: ...
        Source: ...
        Source URL: ...
        """
        lines = [
            f"Competitor: {competitor_name}",
            f"Event Type: {validated['event_type']}",
            f"Event Date: {validated['event_date']}",
            f"Event: {validated['title']}",
            f"Details: {validated['description']}",
            f"Source: {validated['source_name']}",
            f"Source URL: {validated.get('source_url', 'N/A')}"
        ]

        if validated.get("significance"):
            lines.append(f"Significance: {validated['significance']}")

        return "\n".join(lines)

    def create_competitor_event(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Primary ingestion pipeline:
        1. Validates payload and mandatory source requirement.
        2. Resolves or dynamically provisions the competitor in SQLite.
        3. Formats the structured memory representation.
        4. Retains event in competitor's isolated Hindsight memory bank.
        5. Persists structured event in SQLite database.
        6. Returns combined event and Hindsight status verification.
        """
        # 1. Validation
        v = self._validate_event_payload(data)

        # 2. Resolve Competitor
        comp_query = v["competitor_raw"]
        comp = self.db.get_competitor(comp_query)

        if not comp:
            # Dynamically provision competitor profile
            slug = re.sub(r"[^a-zA-Z0-9]+", "-", comp_query.lower()).strip("-")
            hindsight_bank = self.hindsight.get_bank_id_for_competitor(comp_query)
            comp = self.db.upsert_competitor({
                "id": slug,
                "name": comp_query,
                "website": data.get("website", ""),
                "industry": data.get("industry", "Enterprise Technology"),
                "description": f"Dynamically monitored competitor profile for {comp_query}.",
                "hindsight_memory_identifier": hindsight_bank,
                "threat_level": data.get("threat_level", "Medium")
            })
            logger.info(f"Dynamically provisioned competitor profile '{comp['name']}' (ID: {comp['id']})")

        competitor_id = comp["id"]
        competitor_name = comp["name"]

        # 3. Format Context-Rich Memory
        memory_content = self._format_memory_representation(competitor_name, v)

        # 4. Retain in Hindsight
        hindsight_status = "pending"
        hindsight_result = {}

        try:
            hindsight_result = self.hindsight.retain_competitor_event(
                competitor=competitor_name,
                event_data={
                    "title": v["title"],
                    "event_type": v["event_type"],
                    "event_date": v["event_date"],
                    "description": memory_content,
                    "source": v["source_name"]
                }
            )
            hindsight_status = "retained"
            logger.info(f"Retained event into Hindsight bank '{hindsight_result.get('bank_id')}': {v['title']}")

        except (HindsightServiceError, HindsightConfigError, HindsightConnectionError) as herr:
            logger.error(f"Hindsight retention failed: {herr}")
            # Event ingestion fails safely if Hindsight fails
            raise HindsightServiceError(
                message=f"Event could not be retained in Hindsight memory: {herr.message}",
                status_code=herr.status_code,
                details=getattr(herr, "details", str(herr))
            )
        except Exception as e:
            logger.error(f"Unexpected Hindsight error during retention: {e}")
            raise HindsightServiceError(
                message=f"Unexpected error communicating with Hindsight: {str(e)}",
                status_code=502
            )

        # 5. Persist Structured Event in SQLite
        event_id = data.get("id") or f"evt-{uuid.uuid4().hex[:8]}"
        hindsight_bank = hindsight_result.get("bank_id") or comp.get("hindsight_memory_identifier")
        op_id = hindsight_result.get("operation_id") or hindsight_bank

        db_event_record = {
            "id": event_id,
            "competitor_id": competitor_id,
            "event_type": v["event_type"],
            "category": v["event_type"],
            "title": v["title"],
            "description": v["description"],
            "event_date": v["event_date"],
            "source_name": v["source_name"],
            "source_url": v["source_url"],
            "impact": v["impact"],
            "confidence": v["confidence"],
            "evidence_snippet": v["description"][:250],
            "raw_memory_payload": memory_content,
            "hindsight_memory_id": str(op_id),
            "hindsight_status": hindsight_status,
            "metadata": None
        }

        created_event = self.db.upsert_event(db_event_record)

        return {
            "event": created_event,
            "hindsight_status": hindsight_status,
            "hindsight": hindsight_result,
            "competitor": comp
        }

    def get_competitor_events(
        self,
        competitor_id: Optional[str] = None,
        event_type: Optional[str] = None,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None,
        search: Optional[str] = None,
        order_by: str = "desc",
        limit: int = 100
    ) -> List[Dict[str, Any]]:
        """Retrieve events with comprehensive filtering."""
        return self.db.list_events(
            competitor_id=competitor_id,
            event_type=event_type,
            start_date=start_date,
            end_date=end_date,
            search=search,
            order_by=order_by,
            limit=limit
        )

    def get_event_by_id(self, event_id: str) -> Optional[Dict[str, Any]]:
        """Retrieve a single event by ID."""
        return self.db.get_event(event_id)

    def delete_event(self, event_id: str) -> Dict[str, Any]:
        """
        Delete an event from SQLite application database.
        Episodic memories in Hindsight remain immutable unless supported by SDK.
        """
        existing = self.db.get_event(event_id)
        if not existing:
            return {"deleted": False, "found": False, "message": f"Event '{event_id}' not found."}

        deleted = self.db.delete_event(event_id)
        return {
            "deleted": deleted,
            "found": True,
            "deleted_id": event_id,
            "hindsight_note": (
                "Event record removed from SQLite application database. "
                "Episodic memory remains permanently preserved in Hindsight audit ledger "
                "as per immutable competitive intelligence architecture."
            )
        }

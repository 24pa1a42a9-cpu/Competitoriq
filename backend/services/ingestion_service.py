"""
CompetitorIQ Verified Intelligence Ingestion Service
Coordinates external, verified source-backed competitor event ingestion.

Flow:
Real External Source
        ↓
Source-backed Event Payload
        ↓
Event Normalization & Strict Validation
        ↓
Duplicate Protection Check (SQLite lookup)
        ↓
Hindsight RETAIN (Episodic Memory in Competitor Bank)
        ↓
SQLite Persistent Storage (competitor_events table)
        ↓
Verified Intelligence Response
"""

import logging
from typing import Dict, Any, List, Optional
from datetime import datetime
from urllib.parse import urlparse

from services.database_service import DatabaseService
from services.event_service import EventService
from services.hindsight_service import (
    HindsightService,
    HindsightServiceError,
    HindsightConfigError,
    HindsightConnectionError
)
from config.sources import (
    COMPETITOR_SOURCES,
    get_sources_for_competitor,
    is_known_official_domain
)

logger = logging.getLogger("competitoriq.ingestion_service")

# Canonical event categories supported by CompetitorIQ
CANONICAL_EVENT_TYPES = {
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


class IngestionValidationError(Exception):
    """Raised when an incoming event payload fails data quality constraints."""
    def __init__(self, message: str, field: Optional[str] = None):
        super().__init__(message)
        self.message = message
        self.field = field


class IngestionService:
    """
    High-level ingestion pipeline for real-world competitor intelligence.
    Enforces verified source citation, prevents duplicates, coordinates dual
    persistence across SQLite and Hindsight memory.
    """

    def __init__(
        self,
        event_service: Optional[EventService] = None,
        db_service: Optional[DatabaseService] = None,
        hindsight_service: Optional[HindsightService] = None
    ):
        self.db = db_service or DatabaseService()
        self.hindsight = hindsight_service or HindsightService()
        self.event_service = event_service or EventService(
            db_service=self.db,
            hindsight_service=self.hindsight
        )

    def normalize_and_validate(self, raw_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Validates incoming source-backed event and normalizes fields.
        Strictly rejects:
        - empty title
        - empty description
        - invalid date (must be YYYY-MM-DD)
        - invalid or missing competitor
        - invalid event type
        - missing source URL
        - malformed source URL
        """
        if not isinstance(raw_data, dict):
            raise IngestionValidationError("Payload must be a valid JSON object.", field="body")

        # 1. Competitor identification
        raw_competitor = (
            raw_data.get("competitor") or
            raw_data.get("competitor_id") or
            raw_data.get("competitor_name")
        )
        if not raw_competitor or not str(raw_competitor).strip():
            raise IngestionValidationError(
                "The 'competitor' or 'competitor_id' field is required.",
                field="competitor"
            )
        competitor_str = str(raw_competitor).strip()

        # 2. Event Type validation & canonicalization
        raw_type = raw_data.get("event_type") or raw_data.get("category")
        if not raw_type or not str(raw_type).strip():
            raise IngestionValidationError(
                "The 'event_type' field is required. Supported types: " +
                ", ".join(set(CANONICAL_EVENT_TYPES.values())),
                field="event_type"
            )
        norm_type_key = str(raw_type).strip().lower().replace("-", " ")
        if norm_type_key not in CANONICAL_EVENT_TYPES:
            raise IngestionValidationError(
                f"Invalid event_type '{raw_type}'. Supported types: " +
                ", ".join(sorted(set(CANONICAL_EVENT_TYPES.values()))),
                field="event_type"
            )
        canonical_type = CANONICAL_EVENT_TYPES[norm_type_key]

        # 3. Title validation
        title = raw_data.get("title")
        if not title or not str(title).strip():
            raise IngestionValidationError(
                "The 'title' field is required and cannot be empty.",
                field="title"
            )
        title_clean = str(title).strip()

        # 4. Description validation
        description = raw_data.get("description")
        if not description or not str(description).strip():
            raise IngestionValidationError(
                "The 'description' field is required and cannot be empty.",
                field="description"
            )
        description_clean = str(description).strip()

        # 5. Event Date validation (YYYY-MM-DD)
        raw_date = raw_data.get("event_date") or raw_data.get("date")
        if not raw_date or not str(raw_date).strip():
            raise IngestionValidationError(
                "The 'event_date' field is required (YYYY-MM-DD).",
                field="event_date"
            )
        date_clean = str(raw_date).strip().split("T")[0]
        try:
            datetime.strptime(date_clean, "%Y-%m-%d")
        except ValueError:
            raise IngestionValidationError(
                f"Invalid date format '{raw_date}'. Must be in YYYY-MM-DD format.",
                field="event_date"
            )

        # 6. Source Name validation (Mandatory for factual intelligence integrity)
        source_name = raw_data.get("source_name") or raw_data.get("source")
        if not source_name or not str(source_name).strip():
            raise IngestionValidationError(
                "The 'source_name' field is strictly required to ensure verified intelligence integrity.",
                field="source_name"
            )
        source_name_clean = str(source_name).strip()

        # 7. Source URL validation (Mandatory and must be valid HTTP/HTTPS URL)
        source_url = raw_data.get("source_url")
        if not source_url or not str(source_url).strip():
            raise IngestionValidationError(
                "The 'source_url' field is strictly required for verified intelligence events.",
                field="source_url"
            )
        source_url_clean = str(source_url).strip()
        try:
            parsed_url = urlparse(source_url_clean)
            if parsed_url.scheme not in ("http", "https") or not parsed_url.netloc:
                raise ValueError("URL must have valid scheme and network location")
        except Exception:
            raise IngestionValidationError(
                f"Malformed source_url '{source_url_clean}'. Must be a valid URL starting with http:// or https://.",
                field="source_url"
            )

        # Optional intelligence fields
        impact = raw_data.get("impact", "Moderate")
        confidence = raw_data.get("confidence", "95%")
        significance = str(raw_data.get("significance", "")).strip()

        # Check official domain status
        is_official = is_known_official_domain(competitor_str, source_url_clean)

        return {
            "competitor_raw": competitor_str,
            "event_type": canonical_type,
            "title": title_clean,
            "description": description_clean,
            "event_date": date_clean,
            "source_name": source_name_clean,
            "source_url": source_url_clean,
            "impact": impact,
            "confidence": confidence,
            "significance": significance,
            "is_official_source": is_official,
            "id": raw_data.get("id")
        }

    def ingest_event(self, raw_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Primary ingestion pipeline for an individual verified event:
        1. Normalizes and validates incoming payload.
        2. Resolves competitor profile in SQLite.
        3. Checks for duplicate events to prevent double persistence / duplicate memory retention.
        4. Retains formatted structured memory in Hindsight.
        5. Persists structured event record in SQLite database.
        6. Returns full status verification.
        """
        # 1. Validation & Normalization
        v = self.normalize_and_validate(raw_data)

        # 2. Resolve Competitor in SQLite
        comp = self.db.get_competitor(v["competitor_raw"])
        if not comp:
            # Dynamically provision competitor profile if needed
            comp_name = v["competitor_raw"]
            import re
            slug = re.sub(r"[^a-zA-Z0-9]+", "-", comp_name.lower()).strip("-")
            hindsight_bank = self.hindsight.get_bank_id_for_competitor(comp_name)
            comp = self.db.upsert_competitor({
                "id": slug,
                "name": comp_name,
                "website": f"https://{slug}.com",
                "industry": "Enterprise Technology",
                "description": f"Dynamically monitored competitor profile for {comp_name}.",
                "hindsight_memory_identifier": hindsight_bank,
                "threat_level": "Medium"
            })
            logger.info(f"Dynamically provisioned competitor profile '{comp['name']}' ({comp['id']})")

        competitor_id = comp["id"]
        competitor_name = comp["name"]

        # 3. Duplicate Protection Check
        existing_duplicate = self.db.find_duplicate_event(
            competitor_id=competitor_id,
            title=v["title"],
            event_date=v["event_date"],
            source_url=v["source_url"]
        )

        if existing_duplicate:
            logger.info(
                f"Duplicate event detected for {competitor_name}: '{v['title']}' ({v['event_date']}). "
                f"Skipping duplicate SQLite insert and Hindsight memory retention."
            )
            return {
                "status": "duplicate",
                "message": f"Event already exists in competitor intelligence ledger for {competitor_name}.",
                "event": existing_duplicate,
                "competitor": comp,
                "database_status": "already_present",
                "hindsight_status": existing_duplicate.get("hindsight_status", "retained"),
                "source": {
                    "source_name": existing_duplicate.get("source_name"),
                    "source_url": existing_duplicate.get("source_url")
                }
            }

        # 4. Ingest via EventService (coordinates Hindsight RETAIN + SQLite persistence)
        event_payload = {
            "id": v.get("id"),
            "competitor_id": competitor_id,
            "competitor": competitor_name,
            "event_type": v["event_type"],
            "title": v["title"],
            "description": v["description"],
            "event_date": v["event_date"],
            "source_name": v["source_name"],
            "source_url": v["source_url"],
            "impact": v["impact"],
            "confidence": v["confidence"],
            "significance": v["significance"]
        }

        created = self.event_service.create_competitor_event(event_payload)

        return {
            "status": "success",
            "message": "Event successfully verified, persisted in SQLite, and retained in Hindsight memory.",
            "event": created["event"],
            "competitor": comp,
            "database_status": "stored",
            "hindsight_status": created["hindsight_status"],
            "source": {
                "source_name": v["source_name"],
                "source_url": v["source_url"],
                "is_official_domain": v["is_official_source"]
            }
        }

    def ingest_bulk_events(self, raw_events: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Process a batch of events independently.
        One invalid event does not destroy the entire batch.
        Tracks total, successful, duplicates, and failed counts.
        """
        if not isinstance(raw_events, list):
            raise IngestionValidationError("The 'events' field must be an array of event objects.", field="events")

        total = len(raw_events)
        successful = 0
        duplicates = 0
        failed = 0
        results = []

        for index, evt in enumerate(raw_events):
            try:
                outcome = self.ingest_event(evt)
                if outcome.get("status") == "duplicate":
                    duplicates += 1
                else:
                    successful += 1

                results.append({
                    "index": index,
                    "status": outcome.get("status", "success"),
                    "event_id": outcome.get("event", {}).get("id"),
                    "title": outcome.get("event", {}).get("title"),
                    "competitor": outcome.get("competitor", {}).get("name"),
                    "database_status": outcome.get("database_status"),
                    "hindsight_status": outcome.get("hindsight_status"),
                    "message": outcome.get("message")
                })

            except IngestionValidationError as e:
                failed += 1
                results.append({
                    "index": index,
                    "status": "failed",
                    "error": e.message,
                    "field": e.field,
                    "event_title": evt.get("title", f"Event #{index}")
                })

            except (HindsightServiceError, HindsightConfigError, HindsightConnectionError) as herr:
                failed += 1
                results.append({
                    "index": index,
                    "status": "failed",
                    "error": f"Hindsight retention failure: {herr.message}",
                    "event_title": evt.get("title", f"Event #{index}")
                })

            except Exception as e:
                failed += 1
                logger.error(f"Error ingesting event index {index}: {e}")
                results.append({
                    "index": index,
                    "status": "failed",
                    "error": str(e),
                    "event_title": evt.get("title", f"Event #{index}")
                })

        return {
            "total": total,
            "successful": successful,
            "duplicates": duplicates,
            "failed": failed,
            "results": results
        }

    def get_ingestion_status(self) -> Dict[str, Any]:
        """
        Return comprehensive operational status of the ingestion layer:
        - Database connectivity and metrics
        - Hindsight service connectivity
        - Event counts, retention status, pending count
        - Registered official sources
        NO secrets or API keys are exposed.
        """
        db_metrics = self.db.get_ingestion_metrics()
        hindsight_status = self.hindsight.get_status()

        return {
            "status": "operational",
            "database": {
                "connected": True,
                "engine": "SQLite",
                "database_path": self.db.db_path
            },
            "hindsight": {
                "connected": hindsight_status.get("configured", False),
                "base_url": self.hindsight.base_url,
                "status": "active" if hindsight_status.get("configured") else "unconfigured"
            },
            "metrics": {
                "total_competitors": db_metrics["total_competitors"],
                "total_events": db_metrics["total_events"],
                "events_retained": db_metrics["retained_events"],
                "events_pending": db_metrics["pending_events"],
                "competitor_breakdown": db_metrics["competitor_breakdown"],
                "type_breakdown": db_metrics["type_breakdown"]
            },
            "source_registry": {
                "registered_competitors_count": len(COMPETITOR_SOURCES),
                "registered_competitors": list(COMPETITOR_SOURCES.keys())
            }
        }

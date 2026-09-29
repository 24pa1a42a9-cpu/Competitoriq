"""
CompetitorIQ Database Service Layer
Encapsulates all structured data operations against SQLite:
- Competitor directory queries and updates
- Chronological competitor events queries with filtering
- Canonical event types
"""

from typing import List, Optional, Dict, Any
from datetime import datetime
import json
from config import Config
from models.database import get_db_connection
from utils.helpers import row_to_dict


class DatabaseService:
    """Service handling all database queries and transactions."""

    def __init__(self, db_path: Optional[str] = None):
        self.db_path = db_path or Config.DB_PATH

    # --- Competitors ---

    def list_competitors(self) -> List[Dict[str, Any]]:
        """Retrieve all tracked competitors with event counts."""
        with get_db_connection(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute(
                """
                SELECT c.*,
                       (SELECT COUNT(*) FROM competitor_events WHERE competitor_id = c.id) as event_count
                FROM competitors c
                ORDER BY c.name ASC
                """
            )
            rows = cursor.fetchall()
            return [row_to_dict(r) for r in rows]

    def get_competitor(self, competitor_id: str) -> Optional[Dict[str, Any]]:
        """Retrieve a single competitor by ID, slug, or name."""
        with get_db_connection(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute(
                """
                SELECT c.*,
                       (SELECT COUNT(*) FROM competitor_events WHERE competitor_id = c.id) as event_count
                FROM competitors c
                WHERE c.id = ? OR LOWER(c.id) = LOWER(?) OR LOWER(c.name) = LOWER(?)
                """,
                (competitor_id, competitor_id, competitor_id)
            )
            row = cursor.fetchone()
            return row_to_dict(row)

    def upsert_competitor(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Insert or update a competitor record."""
        comp_id = str(data["id"]).strip()
        name = str(data["name"]).strip()
        hindsight_id = data.get("hindsight_memory_identifier") or f"competitor-{comp_id.replace(' ', '-').lower()}"

        with get_db_connection(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute(
                """
                INSERT INTO competitors (
                    id, name, website, industry, description, tagline,
                    hq, founded, stage, arr_estimate, employee_count,
                    primary_battleground, threat_level, strategy_summary,
                    why_this_matters, hindsight_memory_identifier,
                    created_at, updated_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP)
                ON CONFLICT(id) DO UPDATE SET
                    name = excluded.name,
                    website = excluded.website,
                    industry = excluded.industry,
                    description = excluded.description,
                    tagline = excluded.tagline,
                    hq = excluded.hq,
                    founded = excluded.founded,
                    stage = excluded.stage,
                    arr_estimate = excluded.arr_estimate,
                    employee_count = excluded.employee_count,
                    primary_battleground = excluded.primary_battleground,
                    threat_level = excluded.threat_level,
                    strategy_summary = excluded.strategy_summary,
                    why_this_matters = excluded.why_this_matters,
                    hindsight_memory_identifier = excluded.hindsight_memory_identifier,
                    updated_at = CURRENT_TIMESTAMP
                """,
                (
                    comp_id,
                    name,
                    data.get("website"),
                    data.get("industry"),
                    data.get("description"),
                    data.get("tagline"),
                    data.get("hq"),
                    data.get("founded"),
                    data.get("stage"),
                    data.get("arr_estimate"),
                    data.get("employee_count"),
                    data.get("primary_battleground"),
                    data.get("threat_level", "Medium"),
                    data.get("strategy_summary"),
                    data.get("why_this_matters"),
                    hindsight_id
                )
            )
            conn.commit()
            return self.get_competitor(comp_id)

    # --- Events ---

    def list_events(
        self,
        competitor_id: Optional[str] = None,
        event_type: Optional[str] = None,
        category: Optional[str] = None,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None,
        search: Optional[str] = None,
        order_by: str = "desc",
        limit: int = 100
    ) -> List[Dict[str, Any]]:
        """
        Retrieve competitor events with optional filtering by competitor,
        event type, date range, and keyword search.
        """
        with get_db_connection(self.db_path) as conn:
            cursor = conn.cursor()
            query = """
                SELECT e.*, c.name as competitor_name
                FROM competitor_events e
                JOIN competitors c ON e.competitor_id = c.id
                WHERE 1=1
            """
            params = []

            if competitor_id and competitor_id != "all":
                query += " AND (e.competitor_id = ? OR LOWER(c.name) = LOWER(?))"
                params.extend([competitor_id, competitor_id])

            etype = event_type or category
            if etype and etype != "all":
                query += " AND (LOWER(e.event_type) = LOWER(?) OR LOWER(e.category) = LOWER(?))"
                params.extend([etype, etype])

            if start_date:
                query += " AND e.event_date >= ?"
                params.append(start_date)

            if end_date:
                query += " AND e.event_date <= ?"
                params.append(end_date)

            if search:
                query += " AND (e.title LIKE ? OR e.description LIKE ? OR c.name LIKE ?)"
                wildcard = f"%{search}%"
                params.extend([wildcard, wildcard, wildcard])

            sort_order = "ASC" if str(order_by).lower() == "asc" else "DESC"
            query += f" ORDER BY e.event_date {sort_order} LIMIT ?"
            params.append(limit)

            cursor.execute(query, params)
            rows = cursor.fetchall()
            return [row_to_dict(r) for r in rows]

    def get_event(self, event_id: str) -> Optional[Dict[str, Any]]:
        """Retrieve a single event by ID."""
        with get_db_connection(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute(
                """
                SELECT e.*, c.name as competitor_name
                FROM competitor_events e
                JOIN competitors c ON e.competitor_id = c.id
                WHERE e.id = ?
                """,
                (event_id,)
            )
            row = cursor.fetchone()
            return row_to_dict(row)

    def delete_event(self, event_id: str) -> bool:
        """Delete an event from SQLite application database."""
        with get_db_connection(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM competitor_events WHERE id = ?", (event_id,))
            conn.commit()
            return cursor.rowcount > 0

    def create_event(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Record a new verified competitor event."""
        with get_db_connection(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute(
                """
                INSERT INTO competitor_events (
                    id, competitor_id, event_type, category, title, event_date,
                    description, source_name, source_url, impact,
                    confidence, evidence_snippet, raw_memory_payload,
                    hindsight_memory_id, hindsight_status, metadata
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    data["id"],
                    data["competitor_id"],
                    data.get("event_type") or data.get("category", "Other"),
                    data.get("category") or data.get("event_type", "Other"),
                    data["title"],
                    data["event_date"],
                    data.get("description"),
                    data.get("source_name"),
                    data.get("source_url"),
                    data.get("impact", "Moderate"),
                    data.get("confidence", "90%"),
                    data.get("evidence_snippet"),
                    data.get("raw_memory_payload"),
                    data.get("hindsight_memory_id"),
                    data.get("hindsight_status", "retained"),
                    data.get("metadata")
                )
            )
            conn.commit()
            return self.get_event(data["id"])

    def upsert_event(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Insert or update a competitor event record."""
        with get_db_connection(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute(
                """
                INSERT INTO competitor_events (
                    id, competitor_id, event_type, category, title, event_date,
                    description, source_name, source_url, impact,
                    confidence, evidence_snippet, raw_memory_payload,
                    hindsight_memory_id, hindsight_status, metadata
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ON CONFLICT(id) DO UPDATE SET
                    competitor_id = excluded.competitor_id,
                    event_type = excluded.event_type,
                    category = excluded.category,
                    title = excluded.title,
                    event_date = excluded.event_date,
                    description = excluded.description,
                    source_name = excluded.source_name,
                    source_url = excluded.source_url,
                    impact = excluded.impact,
                    confidence = excluded.confidence,
                    evidence_snippet = excluded.evidence_snippet,
                    raw_memory_payload = excluded.raw_memory_payload,
                    hindsight_memory_id = excluded.hindsight_memory_id,
                    hindsight_status = excluded.hindsight_status,
                    metadata = excluded.metadata
                """,
                (
                    data["id"],
                    data["competitor_id"],
                    data.get("event_type") or data.get("category", "Other"),
                    data.get("category") or data.get("event_type", "Other"),
                    data["title"],
                    data["event_date"],
                    data.get("description"),
                    data.get("source_name"),
                    data.get("source_url"),
                    data.get("impact", "Moderate"),
                    data.get("confidence", "90%"),
                    data.get("evidence_snippet"),
                    data.get("raw_memory_payload"),
                    data.get("hindsight_memory_id"),
                    data.get("hindsight_status", "retained"),
                    data.get("metadata")
                )
            )
            conn.commit()
            return self.get_event(data["id"])

    # --- Event Types ---

    def list_event_types(self) -> List[Dict[str, Any]]:
        """Retrieve canonical event categories."""
        with get_db_connection(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM event_types ORDER BY name ASC")
            rows = cursor.fetchall()
            return [row_to_dict(r) for r in rows]

    # --- Duplicate Detection & Ingestion Metrics ---

    def find_duplicate_event(
        self,
        competitor_id: str,
        title: str,
        event_date: str,
        source_url: Optional[str] = None
    ) -> Optional[Dict[str, Any]]:
        """
        Check if an event already exists for a competitor based on:
        1. Exact match of non-empty source_url for this competitor, OR
        2. Exact match of title (normalized) AND event_date for this competitor.
        Prevents duplicate ingestion into SQLite and Hindsight memory.
        """
        with get_db_connection(self.db_path) as conn:
            cursor = conn.cursor()
            s_url = source_url.strip() if source_url else ""
            t_norm = title.strip().lower()

            # First check by source_url if provided
            if s_url:
                cursor.execute(
                    """
                    SELECT e.*, c.name as competitor_name
                    FROM competitor_events e
                    JOIN competitors c ON e.competitor_id = c.id
                    WHERE (e.competitor_id = ? OR LOWER(c.name) = LOWER(?))
                      AND LOWER(e.source_url) = LOWER(?)
                    LIMIT 1
                    """,
                    (competitor_id, competitor_id, s_url)
                )
                row = cursor.fetchone()
                if row:
                    return row_to_dict(row)

            # Second check by competitor + title + event_date
            cursor.execute(
                """
                SELECT e.*, c.name as competitor_name
                FROM competitor_events e
                JOIN competitors c ON e.competitor_id = c.id
                WHERE (e.competitor_id = ? OR LOWER(c.name) = LOWER(?))
                  AND LOWER(TRIM(e.title)) = ?
                  AND e.event_date = ?
                LIMIT 1
                """,
                (competitor_id, competitor_id, t_norm, event_date)
            )
            row = cursor.fetchone()
            return row_to_dict(row)

    def get_ingestion_metrics(self) -> Dict[str, Any]:
        """
        Aggregate event counts, retention metrics, and competitor breakdown.
        Used by the ingestion status monitoring endpoint.
        """
        with get_db_connection(self.db_path) as conn:
            cursor = conn.cursor()

            # Total competitors
            cursor.execute("SELECT COUNT(*) FROM competitors")
            total_competitors = cursor.fetchone()[0]

            # Total events
            cursor.execute("SELECT COUNT(*) FROM competitor_events")
            total_events = cursor.fetchone()[0]

            # Retained events
            cursor.execute("SELECT COUNT(*) FROM competitor_events WHERE LOWER(hindsight_status) = 'retained'")
            retained_events = cursor.fetchone()[0]

            # Pending or failed events
            cursor.execute("SELECT COUNT(*) FROM competitor_events WHERE LOWER(hindsight_status) != 'retained'")
            pending_events = cursor.fetchone()[0]

            # Breakdown by competitor
            cursor.execute("""
                SELECT c.name, COUNT(e.id) as event_count
                FROM competitors c
                LEFT JOIN competitor_events e ON c.id = e.competitor_id
                GROUP BY c.id
                ORDER BY event_count DESC
            """)
            comp_breakdown = {row[0]: row[1] for row in cursor.fetchall()}

            # Breakdown by canonical event_type
            cursor.execute("""
                SELECT COALESCE(event_type, category, 'Other') as etype, COUNT(*) as count
                FROM competitor_events
                GROUP BY etype
                ORDER BY count DESC
            """)
            type_breakdown = {row[0]: row[1] for row in cursor.fetchall()}

            return {
                "total_competitors": total_competitors,
                "total_events": total_events,
                "retained_events": retained_events,
                "pending_events": pending_events,
                "competitor_breakdown": comp_breakdown,
                "type_breakdown": type_breakdown
            }

    # --- Checkpoints (Step 11: "What Changed?" Tracking) ---

    def get_checkpoint(self, competitor_id: str) -> Optional[Dict[str, Any]]:
        """Retrieve the last checked checkpoint for a competitor."""
        with get_db_connection(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute(
                "SELECT * FROM competitor_checkpoints WHERE competitor_id = ?",
                (competitor_id,)
            )
            row = cursor.fetchone()
            return row_to_dict(row)

    def upsert_checkpoint(self, competitor_id: str, last_checked_at: Optional[str] = None) -> Dict[str, Any]:
        """Insert or update a competitor's checkpoint timestamp."""
        ts = last_checked_at or datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")
        with get_db_connection(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute(
                """
                INSERT INTO competitor_checkpoints (competitor_id, last_checked_at, created_at, updated_at)
                VALUES (?, ?, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP)
                ON CONFLICT(competitor_id) DO UPDATE SET
                    last_checked_at = excluded.last_checked_at,
                    updated_at = CURRENT_TIMESTAMP
                """,
                (competitor_id, ts)
            )
            conn.commit()
            return self.get_checkpoint(competitor_id)

    def list_events_since(
        self,
        competitor_id: str,
        since: Optional[str] = None,
        until: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """Retrieve competitor events created or dated on/after a given timestamp or date."""
        with get_db_connection(self.db_path) as conn:
            cursor = conn.cursor()
            query = "SELECT * FROM competitor_events WHERE competitor_id = ?"
            params = [competitor_id]

            if since:
                query += " AND (event_date >= ? OR created_at >= ?)"
                params.extend([since, since])

            if until:
                query += " AND (event_date <= ? OR created_at <= ?)"
                params.extend([until, until])

            query += " ORDER BY event_date ASC, created_at ASC"
            cursor.execute(query, tuple(params))
            rows = cursor.fetchall()
            return [row_to_dict(r) for r in rows]

    # --- Strategic Alerts (Step 11) ---

    def create_alert(self, alert_data: Dict[str, Any]) -> Dict[str, Any]:
        """Persist a new strategic alert in SQLite with duplicate protection."""
        alert_id = alert_data.get("id") or f"alert-{alert_data['competitor_id']}-{int(datetime.utcnow().timestamp())}"
        
        supporting_events_json = json.dumps(alert_data.get("supporting_events") or [])
        memory_used_json = json.dumps(alert_data.get("memory_used") or {})

        with get_db_connection(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute(
                """
                INSERT INTO alerts (
                    id, competitor_id, event_id, title, what_changed, why_it_matters,
                    event_type, severity, confidence, historical_context,
                    supporting_events, memory_used, source_name, source_url,
                    status, detected_at, created_at, updated_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP)
                ON CONFLICT(competitor_id, event_id) DO UPDATE SET
                    title = excluded.title,
                    what_changed = excluded.what_changed,
                    why_it_matters = excluded.why_it_matters,
                    historical_context = excluded.historical_context,
                    supporting_events = excluded.supporting_events,
                    memory_used = excluded.memory_used,
                    updated_at = CURRENT_TIMESTAMP
                """,
                (
                    alert_id,
                    alert_data["competitor_id"],
                    alert_data["event_id"],
                    alert_data["title"],
                    alert_data["what_changed"],
                    alert_data["why_it_matters"],
                    alert_data.get("event_type", "Product"),
                    alert_data.get("severity", "Medium attention"),
                    alert_data.get("confidence", "high"),
                    alert_data.get("historical_context", ""),
                    supporting_events_json,
                    memory_used_json,
                    alert_data.get("source_name", "Official Corporate Source"),
                    alert_data.get("source_url", ""),
                    alert_data.get("status", "new")
                )
            )
            conn.commit()
            return self.get_alert(alert_id)

    def get_alert(self, alert_id: str) -> Optional[Dict[str, Any]]:
        """Retrieve a single alert by ID with parsed JSON fields."""
        with get_db_connection(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute(
                """
                SELECT a.*, c.name as competitor_name
                FROM alerts a
                LEFT JOIN competitors c ON a.competitor_id = c.id
                WHERE a.id = ?
                """,
                (alert_id,)
            )
            row = cursor.fetchone()
            if not row:
                return None
            d = row_to_dict(row)
            if d.get("supporting_events") and isinstance(d["supporting_events"], str):
                try:
                    d["supporting_events"] = json.loads(d["supporting_events"])
                except Exception:
                    pass
            if d.get("memory_used") and isinstance(d["memory_used"], str):
                try:
                    d["memory_used"] = json.loads(d["memory_used"])
                except Exception:
                    pass
            return d

    def get_alert_by_event(self, competitor_id: str, event_id: str) -> Optional[Dict[str, Any]]:
        """Find an alert by competitor and event ID (duplicate prevention)."""
        with get_db_connection(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute(
                "SELECT id FROM alerts WHERE competitor_id = ? AND event_id = ?",
                (competitor_id, event_id)
            )
            row = cursor.fetchone()
            if row:
                return self.get_alert(row[0])
            return None

    def list_alerts(
        self,
        competitor_id: Optional[str] = None,
        status: Optional[str] = None,
        event_type: Optional[str] = None,
        limit: int = 50
    ) -> List[Dict[str, Any]]:
        """Retrieve alerts matching optional filters, ordered by latest detected first."""
        with get_db_connection(self.db_path) as conn:
            cursor = conn.cursor()
            query = """
                SELECT a.*, c.name as competitor_name
                FROM alerts a
                LEFT JOIN competitors c ON a.competitor_id = c.id
                WHERE 1=1
            """
            params = []

            if competitor_id:
                query += " AND (a.competitor_id = ? OR LOWER(c.name) = LOWER(?))"
                params.extend([competitor_id, competitor_id])

            if status:
                query += " AND LOWER(a.status) = LOWER(?)"
                params.append(status)

            if event_type:
                query += " AND LOWER(a.event_type) = LOWER(?)"
                params.append(event_type)

            query += " ORDER BY a.detected_at DESC, a.created_at DESC LIMIT ?"
            params.append(limit)

            cursor.execute(query, tuple(params))
            rows = cursor.fetchall()
            results = []
            for r in rows:
                d = row_to_dict(r)
                if d.get("supporting_events") and isinstance(d["supporting_events"], str):
                    try:
                        d["supporting_events"] = json.loads(d["supporting_events"])
                    except Exception:
                        pass
                if d.get("memory_used") and isinstance(d["memory_used"], str):
                    try:
                        d["memory_used"] = json.loads(d["memory_used"])
                    except Exception:
                        pass
                results.append(d)
            return results

    def update_alert_status(self, alert_id: str, status: str) -> Optional[Dict[str, Any]]:
        """Update an alert's status ('new', 'read', 'dismissed')."""
        with get_db_connection(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute(
                """
                UPDATE alerts
                SET status = ?, updated_at = CURRENT_TIMESTAMP
                WHERE id = ?
                """,
                (status, alert_id)
            )
            conn.commit()
            return self.get_alert(alert_id)

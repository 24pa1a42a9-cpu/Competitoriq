"""
CompetitorIQ Database Layer (SQLite)
Defines the schema and connection lifecycle for structured application data:
- competitors: Monitored companies, profiles, threat metrics
- competitor_events: Tracked chronological moves, sources, dates, categories, evidence
- event_types: Canonical category definitions (Pricing, Product, Hiring, Messaging, etc.)
"""

import sqlite3
import logging
from pathlib import Path

logger = logging.getLogger("competitoriq.database")

SCHEMA_SQL = """
-- Competitors Table
CREATE TABLE IF NOT EXISTS competitors (
    id TEXT PRIMARY KEY,
    name TEXT NOT NULL,
    website TEXT,
    industry TEXT,
    description TEXT,
    tagline TEXT,
    hq TEXT,
    founded TEXT,
    stage TEXT,
    arr_estimate TEXT,
    employee_count TEXT,
    primary_battleground TEXT,
    threat_level TEXT DEFAULT 'Medium',
    strategy_summary TEXT,
    why_this_matters TEXT,
    hindsight_memory_identifier TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Canonical Event Types (Categories)
CREATE TABLE IF NOT EXISTS event_types (
    id TEXT PRIMARY KEY,
    name TEXT NOT NULL UNIQUE,
    description TEXT,
    icon_name TEXT
);

-- Competitor Events Table
CREATE TABLE IF NOT EXISTS competitor_events (
    id TEXT PRIMARY KEY,
    competitor_id TEXT NOT NULL,
    event_type TEXT NOT NULL,
    category TEXT,
    title TEXT NOT NULL,
    description TEXT,
    event_date TEXT NOT NULL,
    source_name TEXT NOT NULL,
    source_url TEXT,
    impact TEXT DEFAULT 'Moderate',
    confidence TEXT DEFAULT '90%',
    evidence_snippet TEXT,
    raw_memory_payload TEXT,
    hindsight_memory_id TEXT,
    hindsight_status TEXT DEFAULT 'retained',
    metadata TEXT, -- JSON string for flexible custom properties
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (competitor_id) REFERENCES competitors(id) ON DELETE CASCADE
);

-- Performance Indexes
CREATE INDEX IF NOT EXISTS idx_events_competitor ON competitor_events(competitor_id);
CREATE INDEX IF NOT EXISTS idx_events_date ON competitor_events(event_date);
CREATE INDEX IF NOT EXISTS idx_events_category ON competitor_events(category);

-- Competitor Checkpoints Table (Step 11: "What Changed?" Tracking)
CREATE TABLE IF NOT EXISTS competitor_checkpoints (
    competitor_id TEXT PRIMARY KEY,
    last_checked_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (competitor_id) REFERENCES competitors(id) ON DELETE CASCADE
);

-- Strategic Competitive Alerts Table (Step 11)
CREATE TABLE IF NOT EXISTS alerts (
    id TEXT PRIMARY KEY,
    competitor_id TEXT NOT NULL,
    event_id TEXT NOT NULL,
    title TEXT NOT NULL,
    what_changed TEXT NOT NULL,
    why_it_matters TEXT NOT NULL,
    event_type TEXT NOT NULL,
    severity TEXT DEFAULT 'Medium attention',
    confidence TEXT DEFAULT 'high',
    historical_context TEXT,
    supporting_events TEXT, -- JSON array of supporting event objects
    memory_used TEXT, -- JSON object of memory count, earliest, latest
    source_name TEXT,
    source_url TEXT,
    status TEXT DEFAULT 'new', -- 'new', 'read', 'dismissed'
    detected_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (competitor_id) REFERENCES competitors(id) ON DELETE CASCADE,
    FOREIGN KEY (event_id) REFERENCES competitor_events(id) ON DELETE CASCADE,
    UNIQUE(competitor_id, event_id)
);

CREATE INDEX IF NOT EXISTS idx_alerts_competitor ON alerts(competitor_id);
CREATE INDEX IF NOT EXISTS idx_alerts_status ON alerts(status);
CREATE INDEX IF NOT EXISTS idx_alerts_event ON alerts(event_id);
"""


def get_db_connection(db_path: str) -> sqlite3.Connection:
    """
    Establish a connection to the SQLite database with Row factory
    to allow column access by name.
    """
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON;")
    return conn


# Canonical Event Types supported by CompetitorIQ
CANONICAL_EVENT_TYPES = [
    ("product", "Product", "Product launches, feature releases, model updates, version debuts", "package"),
    ("pricing", "Pricing", "Price tier adjustments, packaging changes, fee shifts, minimums", "tag"),
    ("hiring", "Hiring", "Executive recruitment, engineering talent acquisition, team expansions", "users"),
    ("partnership", "Partnership", "Strategic alliances, joint ventures, co-sells, platform integrations", "handshake"),
    ("acquisition", "Acquisition", "Corporate mergers, asset acquisitions, team acqui-hires", "briefcase"),
    ("messaging", "Messaging", "Tagline alterations, positioning changes, hero copy diffs, value props", "message-square"),
    ("funding", "Funding", "Venture capital rounds, strategic investments, debt financing", "dollar-sign"),
    ("leadership", "Leadership", "Board appointments, executive departures, reorgs, C-suite changes", "award"),
    ("technology", "Technology", "Infrastructure milestones, benchmark results, patents, research papers", "cpu"),
    ("market_expansion", "Market Expansion", "Geographic expansion, new vertical entry, government cloud authorization", "globe"),
    ("other", "Other", "Regulatory actions, litigation, general announcements, conference talks", "info")
]


def init_db(db_path: str):
    """
    Initializes database tables, runs column migrations, and seeds canonical event types.
    """
    # Ensure directory exists
    Path(db_path).parent.mkdir(parents=True, exist_ok=True)

    with get_db_connection(db_path) as conn:
        conn.executescript(SCHEMA_SQL)

        # 1. Graceful Column Migrations for competitors
        existing_comp_cols = {col[1] for col in conn.execute("PRAGMA table_info(competitors)").fetchall()}
        for col_name, col_type in [
            ("industry", "TEXT"),
            ("description", "TEXT"),
            ("hindsight_memory_identifier", "TEXT")
        ]:
            if col_name not in existing_comp_cols:
                conn.execute(f"ALTER TABLE competitors ADD COLUMN {col_name} {col_type}")

        # 2. Graceful Column Migrations for competitor_events
        existing_event_cols = {col[1] for col in conn.execute("PRAGMA table_info(competitor_events)").fetchall()}
        for col_name, col_type in [
            ("event_type", "TEXT"),
            ("hindsight_status", "TEXT DEFAULT 'retained'")
        ]:
            if col_name not in existing_event_cols:
                conn.execute(f"ALTER TABLE competitor_events ADD COLUMN {col_name} {col_type}")

        # Sync event_type and category if either is null
        conn.execute("UPDATE competitor_events SET event_type = category WHERE event_type IS NULL AND category IS NOT NULL")
        conn.execute("UPDATE competitor_events SET category = event_type WHERE category IS NULL AND event_type IS NOT NULL")

        # Now safe to create index on event_type
        conn.execute("CREATE INDEX IF NOT EXISTS idx_events_type ON competitor_events(event_type)")

        # 3. Seed canonical event types
        for type_id, name, desc, icon in CANONICAL_EVENT_TYPES:
            conn.execute(
                """
                INSERT INTO event_types (id, name, description, icon_name)
                VALUES (?, ?, ?, ?)
                ON CONFLICT(id) DO UPDATE SET
                    name = excluded.name,
                    description = excluded.description,
                    icon_name = excluded.icon_name
                """,
                (type_id, name, desc, icon)
            )

        conn.commit()

    logger.info(f"Database initialized and migrated successfully at {db_path}")

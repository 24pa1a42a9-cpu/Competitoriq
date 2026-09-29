"""
CompetitorIQ Safe Demo Data Cleaning Script (Step 13)
Removes temporary development/test records (NovaAI, CloudMind, TechFlow, TestCorp Alpha/Beta)
from SQLite so the production demo features only real competitors (Microsoft, Google, OpenAI, etc.).
Preserves all Hindsight memory banks intact without deletion.
"""

import sqlite3
import logging
from config import Config

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger("cleanup_demo_data")

TEST_COMPETITOR_IDS = [
    "novaai",
    "cloudmind",
    "techflow",
    "testcorp-alpha",
    "testcorp-beta"
]

def clean_database(db_path: str = Config.DB_PATH):
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    try:
        logger.info(f"Connecting to database at {db_path}...")

        # 1. Clean test alerts
        for cid in TEST_COMPETITOR_IDS:
            cursor.execute("DELETE FROM alerts WHERE competitor_id = ?", (cid,))
            deleted_alerts = cursor.rowcount
            if deleted_alerts > 0:
                logger.info(f"Deleted {deleted_alerts} test alert(s) for {cid}")

        # 2. Clean test checkpoints
        for cid in TEST_COMPETITOR_IDS:
            cursor.execute("DELETE FROM competitor_checkpoints WHERE competitor_id = ?", (cid,))
            deleted_cp = cursor.rowcount
            if deleted_cp > 0:
                logger.info(f"Deleted checkpoint for {cid}")

        # 3. Clean test events
        for cid in TEST_COMPETITOR_IDS:
            cursor.execute("DELETE FROM competitor_events WHERE competitor_id = ?", (cid,))
            deleted_events = cursor.rowcount
            if deleted_events > 0:
                logger.info(f"Deleted {deleted_events} test event(s) for {cid}")

        # 4. Clean test competitors
        for cid in TEST_COMPETITOR_IDS:
            cursor.execute("DELETE FROM competitors WHERE id = ?", (cid,))
            deleted_comp = cursor.rowcount
            if deleted_comp > 0:
                logger.info(f"Deleted test competitor record '{cid}'")

        conn.commit()

        # 5. Verify remaining production competitors
        cursor.execute("SELECT id, name FROM competitors ORDER BY name ASC")
        remaining = cursor.fetchall()
        logger.info("==========================================")
        logger.info(f"Cleaned database successfully! Remaining {len(remaining)} production competitors:")
        for cid, cname in remaining:
            cursor.execute("SELECT COUNT(id) FROM competitor_events WHERE competitor_id = ?", (cid,))
            ev_count = cursor.fetchone()[0]
            logger.info(f"  • {cname:15} (ID: {cid:12}) -> {ev_count} verified events")
        logger.info("==========================================")

    except Exception as e:
        conn.rollback()
        logger.error(f"Error during database cleanup: {e}")
        raise
    finally:
        conn.close()

if __name__ == "__main__":
    clean_database()

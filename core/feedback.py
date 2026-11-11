"""
User Feedback Module (Feature 3)
────────────────────────────────
Allows users to mark emails as "Phishing" or "Safe".
Feedback is stored for analytics only — it NEVER auto-changes
past analysis results.

This module is fully independent — if it fails, the core
system continues to function unaffected.
"""

import sqlite3
import json
from datetime import datetime, timezone

import config


def _get_connection() -> sqlite3.Connection:
    """Get a connection to the shared SQLite database."""
    conn = sqlite3.connect(config.DATABASE_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_feedback_db():
    """Create the user_feedback table if it doesn't exist."""
    conn = _get_connection()
    conn.execute("""
        CREATE TABLE IF NOT EXISTS user_feedback (
            id              INTEGER PRIMARY KEY AUTOINCREMENT,
            message_id      TEXT NOT NULL,
            feedback        TEXT NOT NULL CHECK(feedback IN ('phishing', 'safe')),
            original_score  REAL,
            original_level  TEXT,
            timestamp       TEXT NOT NULL,
            UNIQUE(message_id)
        )
    """)
    conn.commit()
    conn.close()


def submit_feedback(message_id: str, feedback: str,
                    original_score: float = None,
                    original_level: str = None) -> bool:
    """
    Submit user feedback for a specific email.
    Returns True if successfully saved, False if duplicate.

    Args:
        message_id: Gmail message ID
        feedback: 'phishing' or 'safe'
        original_score: The risk score the system originally assigned
        original_level: The risk level the system originally assigned
    """
    if feedback not in ("phishing", "safe"):
        raise ValueError("Feedback must be 'phishing' or 'safe'")

    conn = _get_connection()
    try:
        conn.execute("""
            INSERT INTO user_feedback (message_id, feedback, original_score, original_level, timestamp)
            VALUES (?, ?, ?, ?, ?)
        """, (
            message_id,
            feedback,
            original_score,
            original_level,
            datetime.now(timezone.utc).isoformat(),
        ))
        conn.commit()
        return True
    except sqlite3.IntegrityError:
        # Feedback already exists for this message — update it
        conn.execute("""
            UPDATE user_feedback
            SET feedback = ?, original_score = ?, original_level = ?, timestamp = ?
            WHERE message_id = ?
        """, (
            feedback,
            original_score,
            original_level,
            datetime.now(timezone.utc).isoformat(),
            message_id,
        ))
        conn.commit()
        return True
    finally:
        conn.close()


def get_feedback(message_id: str) -> dict | None:
    """Get feedback for a specific message, or None if not submitted."""
    conn = _get_connection()
    row = conn.execute(
        "SELECT * FROM user_feedback WHERE message_id = ?", (message_id,)
    ).fetchone()
    conn.close()
    return dict(row) if row else None


def get_all_feedback(limit: int = 100) -> list[dict]:
    """Get all feedback entries, newest first."""
    conn = _get_connection()
    rows = conn.execute(
        "SELECT * FROM user_feedback ORDER BY id DESC LIMIT ?", (limit,)
    ).fetchall()
    conn.close()
    return [dict(row) for row in rows]


def get_feedback_stats() -> dict:
    """Get aggregate feedback statistics."""
    conn = _get_connection()

    total = conn.execute("SELECT COUNT(*) as c FROM user_feedback").fetchone()["c"]
    phishing = conn.execute(
        "SELECT COUNT(*) as c FROM user_feedback WHERE feedback = 'phishing'"
    ).fetchone()["c"]
    safe = conn.execute(
        "SELECT COUNT(*) as c FROM user_feedback WHERE feedback = 'safe'"
    ).fetchone()["c"]

    # Count mismatches (system said low risk but user said phishing, or vice versa)
    false_negatives = conn.execute("""
        SELECT COUNT(*) as c FROM user_feedback
        WHERE feedback = 'phishing' AND original_level = 'Low'
    """).fetchone()["c"]

    false_positives = conn.execute("""
        SELECT COUNT(*) as c FROM user_feedback
        WHERE feedback = 'safe' AND original_level = 'High'
    """).fetchone()["c"]

    conn.close()

    return {
        "total": total,
        "marked_phishing": phishing,
        "marked_safe": safe,
        "false_negatives": false_negatives,
        "false_positives": false_positives,
    }


# Initialize table on import
init_feedback_db()

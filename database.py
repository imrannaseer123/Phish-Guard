"""
SQLite Database Module
──────────────────────
Stores analysis logs for the history dashboard.
Privacy-preserving: only stores metadata and findings, not full email bodies.
"""

import sqlite3
import json
from datetime import datetime, timezone

import config


def get_connection() -> sqlite3.Connection:
    """Get a connection to the SQLite database."""
    conn = sqlite3.connect(config.DATABASE_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    """Create the analysis_logs table if it doesn't exist."""
    conn = get_connection()
    conn.execute("""
        CREATE TABLE IF NOT EXISTS analysis_logs (
            id          INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp   TEXT NOT NULL,
            message_id  TEXT,
            sender      TEXT,
            subject     TEXT,
            risk_score  REAL,
            risk_level  TEXT,
            intent      TEXT,
            findings    TEXT,
            summary     TEXT
        )
    """)
    conn.execute("""
        CREATE TABLE IF NOT EXISTS user_risk_trends (
            id          INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp   TEXT NOT NULL,
            risk_score  REAL,
            risk_level  TEXT
        )
    """)
    conn.commit()
    conn.close()


def log_analysis(message_id: str, sender: str, subject: str,
                 risk_score: float, risk_level: str, intent: str,
                 findings_data: list[dict], summary: str):
    """Insert a new analysis record."""
    conn = get_connection()
    conn.execute(
        """INSERT INTO analysis_logs
           (timestamp, message_id, sender, subject, risk_score, risk_level,
            intent, findings, summary)
           VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)""",
        (
            datetime.now(timezone.utc).isoformat(),
            message_id,
            sender,
            subject,
            risk_score,
            risk_level,
            intent,
            json.dumps(findings_data),
            summary,
        ),
    )
    conn.commit()
    conn.close()


def get_history(limit: int = 50) -> list[dict]:
    """Retrieve recent analysis logs, newest first."""
    conn = get_connection()
    rows = conn.execute(
        "SELECT * FROM analysis_logs ORDER BY id DESC LIMIT ?",
        (limit,),
    ).fetchall()
    conn.close()
    return [dict(row) for row in rows]


def get_log_by_id(log_id: int) -> dict | None:
    """Retrieve a single log entry by ID."""
    conn = get_connection()
    row = conn.execute(
        "SELECT * FROM analysis_logs WHERE id = ?", (log_id,)
    ).fetchone()
    conn.close()
    return dict(row) if row else None


def log_risk_trend(risk_score: float, risk_level: str):
    """Log a privacy-safe risk trend data point."""
    conn = get_connection()
    conn.execute(
        "INSERT INTO user_risk_trends (timestamp, risk_score, risk_level) VALUES (?, ?, ?)",
        (datetime.now(timezone.utc).isoformat(), risk_score, risk_level)
    )
    conn.commit()
    conn.close()


def get_risk_trends(limit: int = 100) -> list[dict]:
    """Retrieve recent risk trend data."""
    conn = get_connection()
    rows = conn.execute(
        "SELECT * FROM user_risk_trends ORDER BY id ASC LIMIT ?", # ASC for chronological plotting
        (limit,)
    ).fetchall()
    conn.close()
    return [dict(row) for row in rows]


# Initialize DB on import
init_db()

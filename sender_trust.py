"""
Sender Trust Score Module (Feature 2)
─────────────────────────────────────
Tracks sender/domain reputation locally using a lightweight SQLite table.
Trust score increases for repeated legitimate emails and decreases for
high-risk detections.

IMPORTANT: Trust score influences RECOMMENDATIONS ONLY, never the base
risk score. This module is fully independent — if it fails, the core
system continues to function unaffected.
"""

import sqlite3
import re
from datetime import datetime, timezone

import config


def _get_connection() -> sqlite3.Connection:
    """Get a connection to the shared SQLite database."""
    conn = sqlite3.connect(config.DATABASE_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_trust_db():
    """Create the sender_trust table if it doesn't exist."""
    conn = _get_connection()
    conn.execute("""
        CREATE TABLE IF NOT EXISTS sender_trust (
            domain          TEXT PRIMARY KEY,
            trust_score     REAL NOT NULL DEFAULT 50.0,
            emails_seen     INTEGER NOT NULL DEFAULT 0,
            safe_count      INTEGER NOT NULL DEFAULT 0,
            risky_count     INTEGER NOT NULL DEFAULT 0,
            last_updated    TEXT NOT NULL
        )
    """)
    conn.commit()
    conn.close()


def _extract_domain(sender: str) -> str:
    """Extract the domain from a sender string like 'Name <user@example.com>'."""
    match = re.search(r'@([\w.-]+)', sender)
    return match.group(1).lower() if match else sender.lower().strip()


def get_trust(domain: str) -> dict:
    """
    Get trust data for a sender domain.
    Returns a dict with trust_score, emails_seen, safe_count, risky_count.
    If the domain hasn't been seen before, returns default values.
    """
    conn = _get_connection()
    row = conn.execute(
        "SELECT * FROM sender_trust WHERE domain = ?", (domain,)
    ).fetchone()
    conn.close()

    if row:
        return dict(row)

    return {
        "domain": domain,
        "trust_score": 50.0,
        "emails_seen": 0,
        "safe_count": 0,
        "risky_count": 0,
        "last_updated": None,
    }


def update_trust(sender: str, risk_level: str):
    """
    Update trust score for a sender's domain based on the analysis result.

    Scoring logic:
    - Low risk → trust increases (move toward 100)
    - Medium risk → slight decrease
    - High risk → significant decrease (move toward 0)

    Uses exponential moving average for smooth convergence.
    """
    domain = _extract_domain(sender)
    current = get_trust(domain)

    now = datetime.now(timezone.utc).isoformat()
    emails_seen = current["emails_seen"] + 1
    safe_count = current["safe_count"]
    risky_count = current["risky_count"]
    old_score = current["trust_score"]

    # Determine trust adjustment
    if risk_level == "Low":
        safe_count += 1
        # Move toward 100, with diminishing returns
        adjustment = (100 - old_score) * 0.1
    elif risk_level == "Medium":
        risky_count += 1
        adjustment = -(old_score) * 0.05
    else:  # High
        risky_count += 1
        adjustment = -(old_score) * 0.15

    new_score = max(0.0, min(100.0, old_score + adjustment))

    conn = _get_connection()
    conn.execute("""
        INSERT INTO sender_trust (domain, trust_score, emails_seen, safe_count, risky_count, last_updated)
        VALUES (?, ?, ?, ?, ?, ?)
        ON CONFLICT(domain) DO UPDATE SET
            trust_score = excluded.trust_score,
            emails_seen = excluded.emails_seen,
            safe_count = excluded.safe_count,
            risky_count = excluded.risky_count,
            last_updated = excluded.last_updated
    """, (domain, round(new_score, 1), emails_seen, safe_count, risky_count, now))
    conn.commit()
    conn.close()


def get_trust_recommendation(domain: str) -> dict:
    """
    Generate a trust recommendation for a domain.
    Returns a dict with level, label, description, and color.
    """
    data = get_trust(domain)
    score = data["trust_score"]

    if score >= 75:
        return {
            "level": "trusted",
            "label": "Trusted Sender",
            "description": f"This domain ({domain}) has a strong positive history with {data['safe_count']} safe email(s) observed.",
            "color": "green",
            "score": score,
            "emails_seen": data["emails_seen"],
        }
    elif score >= 40:
        return {
            "level": "neutral",
            "label": "Neutral Reputation",
            "description": f"This domain ({domain}) has limited history. Exercise normal caution.",
            "color": "yellow",
            "score": score,
            "emails_seen": data["emails_seen"],
        }
    else:
        return {
            "level": "untrusted",
            "label": "Low Trust",
            "description": f"This domain ({domain}) has been associated with {data['risky_count']} risky email(s). Be extra cautious.",
            "color": "red",
            "score": score,
            "emails_seen": data["emails_seen"],
        }


# Initialize table on import
init_trust_db()

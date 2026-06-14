"""
ascend Feature 5 — Adaptive Rule Feedback Loop (Explainable)
═══════════════════════════════════════════════════════════════
Provides a feedback system where users can mark ascend analyses
as "Helpful" or "False Alarm". The system collects feedback and
generates explainable weight adjustment *suggestions*.

Boundary: Suggestions are ADVISORY ONLY. The system NEVER
auto-modifies rule weights. All adjustments must be manually
applied by an administrator.
"""

import sqlite3
import json
from datetime import datetime, timezone

import config
from ascend import ascend_config


# ─── Database Setup ───────────────────────────────────────────────────────────

def _get_connection() -> sqlite3.Connection:
    """Get connection to the shared SQLite database."""
    conn = sqlite3.connect(config.DATABASE_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_rule_feedback_db():
    """Create the ascend_rule_feedback table if it doesn't exist."""
    conn = _get_connection()
    conn.execute("""
        CREATE TABLE IF NOT EXISTS ascend_rule_feedback (
            id              INTEGER PRIMARY KEY AUTOINCREMENT,
            message_id      TEXT NOT NULL,
            feedback_type   TEXT NOT NULL CHECK(feedback_type IN ('helpful', 'false_alarm')),
            risk_score      REAL,
            risk_level      TEXT,
            triggered_rules TEXT,
            timestamp       TEXT NOT NULL,
            UNIQUE(message_id)
        )
    """)
    conn.commit()
    conn.close()


# ─── Feedback Operations ─────────────────────────────────────────────────────

def submit_rule_feedback(
    message_id: str,
    feedback_type: str,
    risk_score: float = None,
    risk_level: str = None,
    triggered_rules: list[str] = None,
) -> bool:
    """
    Store user feedback for a specific analysis.

    Args:
        message_id:     Gmail message ID
        feedback_type:  'helpful' or 'false_alarm'
        risk_score:     The risk score from core engine
        risk_level:     The risk level from core engine
        triggered_rules: List of rule/analyzer names that triggered

    Returns:
        True if saved successfully.
    """
    if not ascend_config.RULE_FEEDBACK_ENABLED:
        return False

    if feedback_type not in ("helpful", "false_alarm"):
        raise ValueError("feedback_type must be 'helpful' or 'false_alarm'")

    conn = _get_connection()
    try:
        conn.execute("""
            INSERT INTO ascend_rule_feedback
            (message_id, feedback_type, risk_score, risk_level, triggered_rules, timestamp)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (
            message_id,
            feedback_type,
            risk_score,
            risk_level,
            json.dumps(triggered_rules or []),
            datetime.now(timezone.utc).isoformat(),
        ))
        conn.commit()
        return True
    except sqlite3.IntegrityError:
        # Update existing feedback
        conn.execute("""
            UPDATE ascend_rule_feedback
            SET feedback_type = ?, risk_score = ?, risk_level = ?,
                triggered_rules = ?, timestamp = ?
            WHERE message_id = ?
        """, (
            feedback_type,
            risk_score,
            risk_level,
            json.dumps(triggered_rules or []),
            datetime.now(timezone.utc).isoformat(),
            message_id,
        ))
        conn.commit()
        return True
    finally:
        conn.close()


def get_rule_feedback(message_id: str) -> dict | None:
    """Get feedback for a specific message, or None."""
    conn = _get_connection()
    row = conn.execute(
        "SELECT * FROM ascend_rule_feedback WHERE message_id = ?",
        (message_id,),
    ).fetchone()
    conn.close()
    if row:
        d = dict(row)
        d["triggered_rules"] = json.loads(d.get("triggered_rules", "[]"))
        return d
    return None


def get_all_rule_feedback(limit: int = 100) -> list[dict]:
    """Get all feedback entries, newest first."""
    conn = _get_connection()
    rows = conn.execute(
        "SELECT * FROM ascend_rule_feedback ORDER BY id DESC LIMIT ?",
        (limit,),
    ).fetchall()
    conn.close()
    results = []
    for row in rows:
        d = dict(row)
        d["triggered_rules"] = json.loads(d.get("triggered_rules", "[]"))
        results.append(d)
    return results


# ─── Weight Suggestion Engine ─────────────────────────────────────────────────

def compute_weight_suggestions() -> dict:
    """
    Analyze feedback patterns and generate weight adjustment suggestions.

    Returns:
        {
            "total_feedback": 20,
            "helpful_count": 14,
            "false_alarm_count": 6,
            "suggestions": [
                {
                    "analyzer": "urgency",
                    "current_weight": 15,
                    "suggested_weight": 12,
                    "direction": "decrease",
                    "reason": "3 out of 6 false alarms involved urgency...",
                    "confidence": "Medium",
                },
                ...
            ],
            "summary": "Based on 20 feedback entries...",
        }
    """
    if not ascend_config.RULE_FEEDBACK_ENABLED:
        return {"total_feedback": 0, "suggestions": [],
                "summary": "Feature disabled."}

    all_feedback = get_all_rule_feedback(limit=200)
    if not all_feedback:
        return {
            "total_feedback": 0,
            "helpful_count": 0,
            "false_alarm_count": 0,
            "suggestions": [],
            "summary": "No feedback collected yet. Analyze emails and provide feedback to generate suggestions.",
        }

    helpful = [f for f in all_feedback if f["feedback_type"] == "helpful"]
    false_alarms = [f for f in all_feedback if f["feedback_type"] == "false_alarm"]

    # Count which analyzers appear in false alarms
    fa_analyzer_freq: dict[str, int] = {}
    for fa in false_alarms:
        for rule in fa.get("triggered_rules", []):
            fa_analyzer_freq[rule] = fa_analyzer_freq.get(rule, 0) + 1

    # Count which analyzers appear in helpful feedback
    helpful_analyzer_freq: dict[str, int] = {}
    for h in helpful:
        for rule in h.get("triggered_rules", []):
            helpful_analyzer_freq[rule] = helpful_analyzer_freq.get(rule, 0) + 1

    # Generate suggestions
    suggestions = []
    current_weights = config.SCORE_WEIGHTS

    for analyzer, fa_count in fa_analyzer_freq.items():
        if analyzer not in current_weights:
            continue

        current = current_weights[analyzer]
        helpful_count = helpful_analyzer_freq.get(analyzer, 0)
        total_mentions = fa_count + helpful_count

        if total_mentions == 0:
            continue

        fa_ratio = fa_count / total_mentions

        if fa_ratio >= 0.6 and fa_count >= 3:
            # Strong signal to decrease
            reduction = max(1, int(current * 0.15))
            suggestions.append({
                "analyzer": analyzer,
                "current_weight": current,
                "suggested_weight": current - reduction,
                "direction": "decrease",
                "reason": (
                    f"{fa_count} out of {total_mentions} feedback entries involving "
                    f"'{analyzer}' were false alarms ({fa_ratio:.0%}). "
                    f"Consider reducing weight by {reduction} points."
                ),
                "confidence": "High" if fa_count >= 5 else "Medium",
            })
        elif fa_ratio >= 0.4 and fa_count >= 2:
            # Moderate signal
            reduction = max(1, int(current * 0.10))
            suggestions.append({
                "analyzer": analyzer,
                "current_weight": current,
                "suggested_weight": current - reduction,
                "direction": "decrease",
                "reason": (
                    f"{fa_count} out of {total_mentions} feedback entries involving "
                    f"'{analyzer}' were false alarms ({fa_ratio:.0%}). "
                    f"A slight reduction of {reduction} points may improve accuracy."
                ),
                "confidence": "Low",
            })

    # Check for under-weighted analyzers (high helpful ratio)
    for analyzer, h_count in helpful_analyzer_freq.items():
        if analyzer not in current_weights:
            continue
        if analyzer in fa_analyzer_freq:
            continue  # Already handled above

        if h_count >= 5:
            current = current_weights[analyzer]
            increase = max(1, int(current * 0.10))
            suggestions.append({
                "analyzer": analyzer,
                "current_weight": current,
                "suggested_weight": current + increase,
                "direction": "increase",
                "reason": (
                    f"'{analyzer}' appeared in {h_count} helpful detections "
                    f"with zero false alarms. Consider increasing weight by {increase} points."
                ),
                "confidence": "Medium",
            })

    summary = (
        f"Based on {len(all_feedback)} feedback entries "
        f"({len(helpful)} helpful, {len(false_alarms)} false alarms), "
        f"{len(suggestions)} weight adjustment suggestion{'s' if len(suggestions) != 1 else ''} "
        f"{'were' if len(suggestions) != 1 else 'was'} generated. "
        f"These are advisory only — no weights are automatically changed."
    )

    return {
        "total_feedback": len(all_feedback),
        "helpful_count": len(helpful),
        "false_alarm_count": len(false_alarms),
        "suggestions": suggestions,
        "summary": summary,
    }


# Initialize table on import
init_rule_feedback_db()

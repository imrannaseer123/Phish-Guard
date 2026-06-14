"""
User Risk Profile Modeling Module (Feature 6)
──────────────────────────────────────────────
Creates a user exposure profile by analyzing historical data from
the analysis_logs table:

    - Common attack types targeting the user
    - Risk frequency trends (daily/weekly)
    - Most-targeted intent categories
    - Personal exposure score

This is a READ-ONLY analytics module. It performs no behavioral
automation, sends no alerts, and does not modify any data.

Design Constraints:
    - Reads only from existing analysis_logs table
    - No new database tables required
    - No behavioral automation or action triggers
    - Fail-safe: returns empty profile on error
"""

import sqlite3
import json
from datetime import datetime, timezone, timedelta
from collections import Counter

import config


def _get_connection():
    """Get a connection to the phishing logs database."""
    conn = sqlite3.connect(config.DATABASE_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def get_risk_profile(days=30):
    """
    Compute the user's risk exposure profile from analysis history.

    Parameters
    ----------
    days : int
        Number of days of history to analyze (default: 30).

    Returns
    -------
    dict
        {
            "total_emails_analyzed": int,
            "period_days": int,
            "risk_distribution": {"Low": int, "Medium": int, "High": int},
            "top_intents": [{"intent": str, "count": int, "pct": float}],
            "exposure_score": float,    # 0-100, overall exposure level
            "exposure_label": str,      # "Low" | "Medium" | "High"
            "daily_trend": [{"date": str, "count": int, "avg_score": float}],
            "risk_frequency": {
                "high_per_week": float,
                "medium_per_week": float,
            },
            "top_risky_senders": [{"sender": str, "count": int, "avg_score": float}],
            "most_common_indicators": [{"indicator": str, "count": int}],
            "summary": str,
        }
    """
    try:
        conn = _get_connection()
        cutoff = (datetime.now(timezone.utc) - timedelta(days=days)).isoformat()

        rows = conn.execute("""
            SELECT * FROM analysis_logs
            WHERE timestamp >= ?
            ORDER BY timestamp DESC
        """, (cutoff,)).fetchall()
        conn.close()

        if not rows:
            return _empty_profile(days)

        logs = [dict(r) for r in rows]
        total = len(logs)

        # Risk distribution
        risk_dist = Counter(log["risk_level"] for log in logs)

        # Intent analysis
        intent_counts = Counter(log["intent"] for log in logs)
        top_intents = [
            {
                "intent": intent,
                "count": count,
                "pct": round(count / total * 100, 1),
            }
            for intent, count in intent_counts.most_common(5)
        ]

        # Exposure score: weighted by risk level
        high_count = risk_dist.get("High", 0)
        medium_count = risk_dist.get("Medium", 0)
        low_count = risk_dist.get("Low", 0)

        if total > 0:
            exposure_score = min(100, round(
                (high_count * 3 + medium_count * 1.5) / total * 33.3, 1
            ))
        else:
            exposure_score = 0.0

        if exposure_score >= 60:
            exposure_label = "High"
        elif exposure_score >= 30:
            exposure_label = "Medium"
        else:
            exposure_label = "Low"

        # Daily trend
        daily_data = {}
        for log in logs:
            date_str = log["timestamp"][:10]  # YYYY-MM-DD
            if date_str not in daily_data:
                daily_data[date_str] = {"count": 0, "total_score": 0}
            daily_data[date_str]["count"] += 1
            daily_data[date_str]["total_score"] += (log["risk_score"] or 0)

        daily_trend = sorted([
            {
                "date": date,
                "count": data["count"],
                "avg_score": round(data["total_score"] / data["count"], 1),
            }
            for date, data in daily_data.items()
        ], key=lambda x: x["date"])

        # Risk frequency per week
        weeks = max(1, days / 7)
        risk_frequency = {
            "high_per_week": round(high_count / weeks, 1),
            "medium_per_week": round(medium_count / weeks, 1),
        }

        # Top risky senders
        sender_data = {}
        for log in logs:
            sender = log.get("sender", "Unknown")
            score = log.get("risk_score", 0) or 0
            if score >= config.RISK_LOW_MAX:
                if sender not in sender_data:
                    sender_data[sender] = {"count": 0, "total_score": 0}
                sender_data[sender]["count"] += 1
                sender_data[sender]["total_score"] += score

        top_risky = sorted(
            [
                {
                    "sender": sender,
                    "count": data["count"],
                    "avg_score": round(data["total_score"] / data["count"], 1),
                }
                for sender, data in sender_data.items()
            ],
            key=lambda x: x["count"],
            reverse=True,
        )[:5]

        # Most common indicators from findings
        indicator_counter = Counter()
        for log in logs:
            try:
                findings = json.loads(log.get("findings", "[]"))
                for f in findings:
                    indicator_counter[f.get("indicator", "unknown")] += 1
            except (json.JSONDecodeError, TypeError):
                pass

        common_indicators = [
            {"indicator": ind, "count": cnt}
            for ind, cnt in indicator_counter.most_common(10)
        ]

        summary = _generate_profile_summary(
            total, risk_dist, exposure_score, exposure_label,
            top_intents, days
        )

        return {
            "total_emails_analyzed": total,
            "period_days": days,
            "risk_distribution": dict(risk_dist),
            "top_intents": top_intents,
            "exposure_score": exposure_score,
            "exposure_label": exposure_label,
            "daily_trend": daily_trend,
            "risk_frequency": risk_frequency,
            "top_risky_senders": top_risky,
            "most_common_indicators": common_indicators,
            "summary": summary,
        }

    except Exception:
        return _empty_profile(days)


def _generate_profile_summary(total, risk_dist, exposure_score,
                               exposure_label, top_intents, days):
    """Generate a human-readable risk profile summary."""
    high = risk_dist.get("High", 0)
    medium = risk_dist.get("Medium", 0)

    if total == 0:
        return f"No emails analyzed in the past {days} days."

    top_intent = top_intents[0]["intent"] if top_intents else "Unknown"

    if exposure_label == "High":
        return (
            f"⚠️ High exposure: {high} high-risk and {medium} medium-risk "
            f"emails detected out of {total} analyzed in {days} days. "
            f"The most common attack type is '{top_intent}'. "
            f"Consider enhanced email filtering."
        )

    if exposure_label == "Medium":
        return (
            f"Moderate exposure: {high + medium} risky emails detected "
            f"out of {total} analyzed in {days} days. "
            f"Most common intent: '{top_intent}'. Stay vigilant."
        )

    return (
        f"Low exposure: Most emails ({total - high - medium}/{total}) are safe. "
        f"Your email risk profile over the past {days} days is healthy."
    )


def _empty_profile(days):
    """Return an empty profile structure."""
    return {
        "total_emails_analyzed": 0,
        "period_days": days,
        "risk_distribution": {},
        "top_intents": [],
        "exposure_score": 0,
        "exposure_label": "Low",
        "daily_trend": [],
        "risk_frequency": {"high_per_week": 0, "medium_per_week": 0},
        "top_risky_senders": [],
        "most_common_indicators": [],
        "summary": f"No emails analyzed in the past {days} days.",
    }

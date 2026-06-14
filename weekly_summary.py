"""
Weekly Security Summary Module (Feature 5)
──────────────────────────────────────────
Generates weekly statistics from the analysis_logs table:
- Emails scanned
- High-risk count
- Most common phishing intent
- Risk score distribution
- Top risky senders

This is a READ-ONLY analytics module. It queries existing data
without modifying anything. Fully independent and fail-safe.
"""

import json
import re
from datetime import datetime, timezone, timedelta
from collections import Counter

import database


def get_weekly_summary(days: int = 7) -> dict:
    """
    Compute security summary statistics for the last N days.

    Returns a dict with all relevant dashboard metrics.
    """
    cutoff = (datetime.now(timezone.utc) - timedelta(days=days)).isoformat()

    conn = database.get_connection()

    # All logs from the period
    rows = conn.execute(
        "SELECT * FROM analysis_logs WHERE timestamp >= ? ORDER BY timestamp DESC",
        (cutoff,)
    ).fetchall()
    logs = [dict(r) for r in rows]

    # All-time totals for comparison
    total_all_time = conn.execute(
        "SELECT COUNT(*) as c FROM analysis_logs"
    ).fetchone()["c"]

    conn.close()

    if not logs:
        return _empty_summary(days, total_all_time)

    # ── Core Metrics ──
    total_scanned = len(logs)
    risk_levels = [log["risk_level"] for log in logs]
    high_risk_count = risk_levels.count("High")
    medium_risk_count = risk_levels.count("Medium")
    low_risk_count = risk_levels.count("Low")

    # ── Intent Distribution ──
    intents = [log["intent"] for log in logs if log.get("intent")]
    intent_counts = Counter(intents)
    most_common_intent = intent_counts.most_common(1)[0] if intent_counts else ("N/A", 0)

    # ── Average Risk Score ──
    scores = [log["risk_score"] for log in logs if log.get("risk_score") is not None]
    avg_score = round(sum(scores) / len(scores), 1) if scores else 0

    # ── Top Risky Senders ──
    risky_senders = Counter()
    for log in logs:
        if log.get("risk_level") in ("Medium", "High"):
            sender = log.get("sender", "Unknown")
            risky_senders[sender] += 1
    top_risky_senders = risky_senders.most_common(5)

    # ── Daily Breakdown (for chart) ──
    daily_counts = {}
    daily_risk = {}
    for i in range(days):
        day = (datetime.now(timezone.utc) - timedelta(days=i)).strftime("%Y-%m-%d")
        daily_counts[day] = 0
        daily_risk[day] = 0

    for log in logs:
        day = log["timestamp"][:10]
        if day in daily_counts:
            daily_counts[day] += 1
            if log.get("risk_level") in ("Medium", "High"):
                daily_risk[day] += 1

    # Sort by date
    sorted_days = sorted(daily_counts.keys())
    daily_labels = sorted_days
    daily_scan_values = [daily_counts[d] for d in sorted_days]
    daily_risk_values = [daily_risk[d] for d in sorted_days]

    # ── Recent High-Risk Alerts ──
    recent_alerts = [
        {
            "sender": log.get("sender", "Unknown"),
            "subject": log.get("subject", "No subject"),
            "score": log.get("risk_score", 0),
            "intent": log.get("intent", "Unknown"),
            "timestamp": log.get("timestamp", "")[:19],
        }
        for log in logs
        if log.get("risk_level") == "High"
    ][:10]

    # ── Targeted Brand Frequency ──
    brand_counter = Counter()
    known_brands = [
        "paypal", "apple", "microsoft", "google", "amazon", "netflix",
        "facebook", "instagram", "whatsapp", "linkedin", "twitter",
        "chase", "wells fargo", "bank of america", "citibank", "hsbc",
        "dhl", "fedex", "ups", "usps", "irs", "dropbox", "docusign",
    ]
    for log in logs:
        findings_raw = log.get("findings", "")
        if findings_raw:
            try:
                findings = json.loads(findings_raw) if isinstance(findings_raw, str) else findings_raw
                for f in findings:
                    evidence = (f.get("evidence", "") or "").lower()
                    for brand in known_brands:
                        if brand in evidence:
                            brand_counter[brand.title()] += 1
            except (json.JSONDecodeError, TypeError):
                pass
    top_brands = brand_counter.most_common(8)

    # ── Daily Intent Breakdown (for trend chart) ──
    daily_intent = {}  # {date: {intent: count}}
    for log in logs:
        day = log["timestamp"][:10]
        intent = log.get("intent", "Unknown")
        if day not in daily_intent:
            daily_intent[day] = Counter()
        daily_intent[day][intent] += 1

    # Build sorted structure for template
    all_intents = sorted(set(intents)) if intents else []
    daily_intent_data = {
        "labels": sorted_days,
        "intents": all_intents,
        "series": {
            intent: [daily_intent.get(d, {}).get(intent, 0) for d in sorted_days]
            for intent in all_intents
        },
    }

    return {
        "period_days": days,
        "total_scanned": total_scanned,
        "total_all_time": total_all_time,
        "high_risk_count": high_risk_count,
        "medium_risk_count": medium_risk_count,
        "low_risk_count": low_risk_count,
        "avg_score": avg_score,
        "most_common_intent": most_common_intent[0],
        "most_common_intent_count": most_common_intent[1],
        "intent_distribution": dict(intent_counts),
        "top_risky_senders": top_risky_senders,
        "daily_labels": daily_labels,
        "daily_scan_values": daily_scan_values,
        "daily_risk_values": daily_risk_values,
        "recent_alerts": recent_alerts,
        "top_brands": top_brands,
        "daily_intent_data": daily_intent_data,
    }


def _empty_summary(days: int, total_all_time: int) -> dict:
    """Return an empty summary when no data exists for the period."""
    return {
        "period_days": days,
        "total_scanned": 0,
        "total_all_time": total_all_time,
        "high_risk_count": 0,
        "medium_risk_count": 0,
        "low_risk_count": 0,
        "avg_score": 0,
        "most_common_intent": "N/A",
        "most_common_intent_count": 0,
        "intent_distribution": {},
        "top_risky_senders": [],
        "daily_labels": [],
        "daily_scan_values": [],
        "daily_risk_values": [],
        "recent_alerts": [],
        "top_brands": [],
        "daily_intent_data": {"labels": [], "intents": [], "series": {}},
    }

"""
ascend Feature 3 — Human Risk Forecasting (Non-ML)
════════════════════════════════════════════════════════
Computes a user-level vulnerability profile using:
  • Simple Moving Average (SMA) of recent risk scores
  • Frequency of high-risk emails
  • Trend direction (rising / stable / falling)

Output is READ-ONLY and advisory — never modifies data.

Boundary: Reads from existing analysis_logs table via
database.get_history(). No new DB writes.
"""

import json
from ascend import ascend_config


def compute_risk_forecast(history: list[dict]) -> dict:
    """
    Compute user vulnerability forecast from analysis history.

    Args:
        history: List of analysis log dicts from database.get_history().
                 Each dict has: risk_score, risk_level, timestamp, etc.

    Returns:
        {
            "vulnerability_level": "Low" | "Medium" | "High",
            "confidence_explanation": "...",
            "trend_direction": "rising" | "stable" | "falling",
            "stats": {
                "total_analyses": 15,
                "avg_risk_score": 42.3,
                "high_risk_count": 3,
                "high_risk_ratio": 0.2,
                "recent_avg": 55.0,
                "overall_avg": 42.3,
            }
        }
    """
    if not ascend_config.RISK_FORECAST_ENABLED:
        return _empty_forecast("Feature disabled.")

    if not history:
        return _empty_forecast("No analysis history available for forecasting.")

    # ── Extract risk scores (most recent first, as returned by get_history) ──
    scores = []
    for entry in history:
        score = entry.get("risk_score")
        if score is not None:
            scores.append(float(score))

    if not scores:
        return _empty_forecast("No valid risk scores in history.")

    total = len(scores)
    window = min(ascend_config.FORECAST_WINDOW, total)

    # ── Compute statistics ──
    overall_avg = sum(scores) / total
    recent_scores = scores[:window]  # Most recent N scores
    recent_avg = sum(recent_scores) / len(recent_scores)

    # Count high-risk emails
    high_risk_count = sum(1 for s in scores if s > 66)
    high_risk_ratio = high_risk_count / total

    # ── Determine trend direction ──
    if len(recent_scores) >= 4:
        first_half = recent_scores[len(recent_scores)//2:]  # Older half
        second_half = recent_scores[:len(recent_scores)//2]  # Newer half
        first_avg = sum(first_half) / len(first_half)
        second_avg = sum(second_half) / len(second_half)
        diff = second_avg - first_avg
        if diff > 5:
            trend = "rising"
        elif diff < -5:
            trend = "falling"
        else:
            trend = "stable"
    else:
        trend = "stable"

    # ── Classify vulnerability level ──
    vuln_level, confidence = _classify_vulnerability(
        recent_avg, high_risk_ratio, trend, total
    )

    stats = {
        "total_analyses": total,
        "avg_risk_score": round(overall_avg, 1),
        "high_risk_count": high_risk_count,
        "high_risk_ratio": round(high_risk_ratio, 3),
        "recent_avg": round(recent_avg, 1),
        "overall_avg": round(overall_avg, 1),
    }

    return {
        "vulnerability_level": vuln_level,
        "confidence_explanation": confidence,
        "trend_direction": trend,
        "stats": stats,
    }


def _classify_vulnerability(
    recent_avg: float,
    high_risk_ratio: float,
    trend: str,
    sample_size: int,
) -> tuple[str, str]:
    """
    Classify user vulnerability and generate confidence explanation.

    Returns:
        (level, explanation) tuple.
    """
    reasons = []

    # ── Score-based signals ──
    score_signal = 0
    if recent_avg >= 60:
        score_signal = 2
        reasons.append(f"Recent average risk score is high ({recent_avg:.0f}/100)")
    elif recent_avg >= 35:
        score_signal = 1
        reasons.append(f"Recent average risk score is moderate ({recent_avg:.0f}/100)")
    else:
        reasons.append(f"Recent average risk score is low ({recent_avg:.0f}/100)")

    # ── Frequency-based signals ──
    freq_signal = 0
    if high_risk_ratio >= ascend_config.FORECAST_HIGH_FREQ_THRESHOLD:
        freq_signal = 2
        reasons.append(
            f"{high_risk_ratio:.0%} of emails received were high-risk "
            f"(threshold: {ascend_config.FORECAST_HIGH_FREQ_THRESHOLD:.0%})"
        )
    elif high_risk_ratio >= 0.2:
        freq_signal = 1
        reasons.append(f"{high_risk_ratio:.0%} of emails received were high-risk")

    # ── Trend-based signals ──
    trend_signal = 0
    if trend == "rising":
        trend_signal = 1
        reasons.append("Risk trend is rising — vulnerability may be increasing")
    elif trend == "falling":
        trend_signal = -1
        reasons.append("Risk trend is falling — positive improvement observed")

    # ── Composite decision ──
    composite = score_signal + freq_signal + trend_signal

    if composite >= 3:
        level = "High"
    elif composite >= 1:
        level = "Medium"
    else:
        level = "Low"

    # ── Confidence qualifier ──
    if sample_size < 5:
        confidence_note = (
            f"(Low confidence: based on only {sample_size} "
            f"analys{'e' if sample_size == 1 else 'e'}s. "
            f"More data will improve accuracy.)"
        )
    elif sample_size < 15:
        confidence_note = f"(Moderate confidence: based on {sample_size} analyses.)"
    else:
        confidence_note = f"(High confidence: based on {sample_size} analyses.)"

    explanation = " | ".join(reasons) + f" {confidence_note}"
    return level, explanation


def _empty_forecast(reason: str) -> dict:
    """Return an empty forecast result."""
    return {
        "vulnerability_level": "Unknown",
        "confidence_explanation": reason,
        "trend_direction": "stable",
        "stats": {
            "total_analyses": 0,
            "avg_risk_score": 0,
            "high_risk_count": 0,
            "high_risk_ratio": 0,
            "recent_avg": 0,
            "overall_avg": 0,
        },
    }

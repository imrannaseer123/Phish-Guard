"""
Adaptive Analyzer Weight Suggestions Module (Feature 4)
───────────────────────────────────────────────────────
Computes suggested analyzer weight adjustments based on user feedback
and analysis history. Suggestions are DISPLAY-ONLY and never auto-applied.

This module is fully independent — if it fails, the core system
continues to function unaffected.
"""

import json
from collections import defaultdict

import config
import database
import feedback as feedback_module


def compute_weight_suggestions() -> dict:
    """
    Analyze feedback history to suggest weight adjustments.

    Logic:
    - If users frequently mark low-risk emails as phishing → some analyzers
      are under-weighting. Suggest increasing those weights.
    - If users frequently mark high-risk emails as safe → some analyzers
      are over-weighting. Suggest decreasing those weights.

    Returns a dict with current weights, suggested weights, and explanations.
    """
    current_weights = dict(config.SCORE_WEIGHTS)
    suggestions = {}
    explanations = {}

    # Get all feedback entries
    all_feedback = feedback_module.get_all_feedback(limit=500)
    if not all_feedback:
        return {
            "current_weights": current_weights,
            "suggested_weights": current_weights.copy(),
            "explanations": {k: "No feedback data yet — collect more feedback for meaningful suggestions." for k in current_weights},
            "confidence": "low",
            "total_feedback": 0,
        }

    # Analyze mismatches
    false_negatives = []  # system said safe, user said phishing
    false_positives = []  # system said risky, user said safe
    correct = []           # system and user agree

    for fb in all_feedback:
        msg_id = fb["message_id"]
        # Find matching analysis log
        log = _find_analysis_log(msg_id)
        if not log:
            continue

        if fb["feedback"] == "phishing" and fb.get("original_level") == "Low":
            false_negatives.append(log)
        elif fb["feedback"] == "safe" and fb.get("original_level") in ("Medium", "High"):
            false_positives.append(log)
        else:
            correct.append(log)

    # Compute per-analyzer contribution in mismatched cases
    fn_analyzer_scores = _aggregate_analyzer_scores(false_negatives)
    fp_analyzer_scores = _aggregate_analyzer_scores(false_positives)

    for analyzer, current_weight in current_weights.items():
        suggested = current_weight
        explanation_parts = []

        # False negatives → analyzer didn't catch enough → increase weight
        if false_negatives:
            fn_avg = fn_analyzer_scores.get(analyzer, 0)
            if fn_avg < current_weight * 0.3:
                increase = min(5, round(current_weight * 0.15))
                suggested += increase
                explanation_parts.append(
                    f"Under-detecting in {len(false_negatives)} missed phishing emails "
                    f"(avg contribution: {fn_avg:.1f}/{current_weight}). "
                    f"Suggest +{increase} pts."
                )

        # False positives → analyzer is too sensitive → decrease weight
        if false_positives:
            fp_avg = fp_analyzer_scores.get(analyzer, 0)
            if fp_avg > current_weight * 0.6:
                decrease = min(5, round(current_weight * 0.1))
                suggested -= decrease
                explanation_parts.append(
                    f"Over-flagging in {len(false_positives)} safe emails "
                    f"(avg contribution: {fp_avg:.1f}/{current_weight}). "
                    f"Suggest -{decrease} pts."
                )

        # Ensure suggested stays in reasonable bounds
        suggested = max(5, min(40, suggested))
        suggestions[analyzer] = suggested

        if explanation_parts:
            explanations[analyzer] = " | ".join(explanation_parts)
        else:
            explanations[analyzer] = "Current weight appears well-calibrated based on feedback."

    # Determine confidence level
    total = len(all_feedback)
    if total >= 20:
        confidence = "high"
    elif total >= 5:
        confidence = "medium"
    else:
        confidence = "low"

    return {
        "current_weights": current_weights,
        "suggested_weights": suggestions,
        "explanations": explanations,
        "confidence": confidence,
        "total_feedback": total,
        "false_negatives": len(false_negatives),
        "false_positives": len(false_positives),
        "correct_predictions": len(correct),
    }


def _find_analysis_log(message_id: str) -> dict | None:
    """Find the analysis log entry for a given message ID."""
    conn = database.get_connection()
    row = conn.execute(
        "SELECT * FROM analysis_logs WHERE message_id = ?", (message_id,)
    ).fetchone()
    conn.close()
    return dict(row) if row else None


def _aggregate_analyzer_scores(logs: list[dict]) -> dict[str, float]:
    """Compute average per-analyzer scores across a list of analysis logs."""
    if not logs:
        return {}

    totals = defaultdict(float)
    count = 0

    for log in logs:
        try:
            findings = json.loads(log.get("findings", "[]"))
            for finding in findings:
                totals[finding["analyzer"]] += finding["score"]
            count += 1
        except (json.JSONDecodeError, KeyError):
            continue

    if count == 0:
        return {}

    return {k: round(v / count, 1) for k, v in totals.items()}

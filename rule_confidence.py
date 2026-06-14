"""
Rule Confidence Scoring Module (Feature 9)
──────────────────────────────────────────
Computes historical confidence scores for each detection rule.

Methodology:
    1. Reads all past analysis_logs to count how often each indicator
       appears across analyses.
    2. Cross-references with user_feedback (if available) to determine
       how often each indicator's detection correlates with confirmed
       phishing vs. false positives.
    3. Computes a confidence percentage per indicator.

Confidence Formula:
    base_confidence = min(95, 50 + log2(appearance_count) * 10)
    If feedback available:
        adjusted = base * (confirmed_phishing / total_feedback)

The confidence represents "how reliably this rule identifies actual
phishing" based on historical evidence.

Design Constraints:
    - Read-only: queries existing tables only
    - Display-only: shown alongside findings
    - No modifications to detection logic or scores
    - Fail-safe: returns default confidence on error
"""

import sqlite3
import json
import math
from collections import Counter

import config


def _get_connection():
    """Get a connection to the phishing logs database."""
    conn = sqlite3.connect(config.DATABASE_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def compute_rule_confidence():
    """
    Compute confidence scores for all detection rules based on
    historical analysis data.

    Returns
    -------
    dict[str, dict]
        Maps indicator names to confidence data:
        {
            "indicator_name": {
                "confidence_pct": float,     # 0-100
                "confidence_label": str,     # "Low" | "Medium" | "High"
                "appearances": int,          # Total appearances in history
                "feedback_alignment": float, # -1 to 1 (if feedback available)
                "explanation": str,
            },
            ...
        }
    """
    try:
        # Count indicator appearances across all analyses
        indicator_counts = _count_indicator_appearances()

        # Get feedback correlation (if table exists)
        feedback_data = _get_feedback_correlation()

        # Compute confidence for each indicator
        confidences = {}
        for indicator, count in indicator_counts.items():
            # Base confidence: logarithmic growth from appearances
            if count >= 1:
                base_conf = min(95.0, 50.0 + math.log2(count + 1) * 10.0)
            else:
                base_conf = 30.0

            # Adjust with feedback if available
            feedback_alignment = 0.0
            if indicator in feedback_data:
                fb = feedback_data[indicator]
                if fb["total"] > 0:
                    # Alignment: how often users confirmed this as phishing
                    feedback_alignment = (
                        (fb["confirmed_phishing"] - fb["false_positive"])
                        / fb["total"]
                    )
                    # Boost or penalize confidence based on alignment
                    adjustment = feedback_alignment * 20.0
                    base_conf = max(10.0, min(98.0, base_conf + adjustment))

            confidence_pct = round(base_conf, 1)

            # Assign label
            if confidence_pct >= 75:
                label = "High"
            elif confidence_pct >= 50:
                label = "Medium"
            else:
                label = "Low"

            explanation = _generate_explanation(
                indicator, count, confidence_pct, label, feedback_alignment
            )

            confidences[indicator] = {
                "confidence_pct": confidence_pct,
                "confidence_label": label,
                "appearances": count,
                "feedback_alignment": round(feedback_alignment, 2),
                "explanation": explanation,
            }

        return confidences

    except Exception:
        return {}


def get_finding_confidence(indicator_name, all_confidences=None):
    """
    Get the confidence score for a specific indicator/rule.

    Parameters
    ----------
    indicator_name : str
        The indicator to look up.
    all_confidences : dict, optional
        Pre-computed confidences to avoid re-querying.

    Returns
    -------
    dict
        Confidence data for the indicator, or default if not found.
    """
    try:
        if all_confidences is None:
            all_confidences = compute_rule_confidence()

        if indicator_name in all_confidences:
            return all_confidences[indicator_name]

        # Default for unknown indicators
        return {
            "confidence_pct": 50.0,
            "confidence_label": "Medium",
            "appearances": 0,
            "feedback_alignment": 0.0,
            "explanation": (
                f"No historical data available for '{indicator_name}'. "
                f"Default confidence assigned."
            ),
        }

    except Exception:
        return {
            "confidence_pct": 50.0,
            "confidence_label": "Medium",
            "appearances": 0,
            "feedback_alignment": 0.0,
            "explanation": "Confidence computation unavailable.",
        }


def _count_indicator_appearances():
    """Count how many times each indicator appears across all analyses."""
    try:
        conn = _get_connection()
        rows = conn.execute("""
            SELECT findings FROM analysis_logs
            WHERE findings IS NOT NULL
        """).fetchall()
        conn.close()

        counter = Counter()
        for row in rows:
            try:
                findings = json.loads(row["findings"])
                for f in findings:
                    indicator = f.get("indicator", "")
                    if indicator:
                        counter[indicator] += 1
            except (json.JSONDecodeError, TypeError):
                pass

        return dict(counter)

    except Exception:
        return {}


def _get_feedback_correlation():
    """
    Cross-reference indicators with user feedback to determine accuracy.

    Only works if the user_feedback table exists (Feature 3 from v1).
    Fails silently if the table doesn't exist.
    """
    try:
        conn = _get_connection()

        # Check if user_feedback table exists
        table_check = conn.execute("""
            SELECT name FROM sqlite_master
            WHERE type='table' AND name='user_feedback'
        """).fetchone()

        if not table_check:
            conn.close()
            return {}

        # Join feedback with analysis logs
        rows = conn.execute("""
            SELECT al.findings, uf.feedback
            FROM user_feedback uf
            JOIN analysis_logs al ON al.message_id = uf.message_id
        """).fetchall()
        conn.close()

        correlation = {}
        for row in rows:
            try:
                findings = json.loads(row["findings"])
                feedback = row["feedback"]

                for f in findings:
                    indicator = f.get("indicator", "")
                    if not indicator:
                        continue
                    if indicator not in correlation:
                        correlation[indicator] = {
                            "confirmed_phishing": 0,
                            "false_positive": 0,
                            "total": 0,
                        }

                    correlation[indicator]["total"] += 1
                    if feedback == "phishing":
                        correlation[indicator]["confirmed_phishing"] += 1
                    elif feedback == "safe":
                        correlation[indicator]["false_positive"] += 1

            except (json.JSONDecodeError, TypeError):
                pass

        return correlation

    except Exception:
        return {}


def _generate_explanation(indicator, count, confidence, label, alignment):
    """Generate a human-readable explanation for a rule's confidence."""
    # Pretty-print indicator name
    display_name = indicator.replace("_", " ").title()

    parts = [f"'{display_name}' has appeared in {count} analysis(es)."]

    if confidence >= 75:
        parts.append(
            f"High confidence ({confidence}%) — this rule reliably "
            f"identifies suspicious patterns."
        )
    elif confidence >= 50:
        parts.append(
            f"Medium confidence ({confidence}%) — this rule has "
            f"moderate historical reliability."
        )
    else:
        parts.append(
            f"Low confidence ({confidence}%) — limited historical data "
            f"makes this rule's reliability uncertain."
        )

    if alignment > 0.3:
        parts.append("User feedback strongly supports this detection.")
    elif alignment < -0.3:
        parts.append("User feedback suggests this rule may over-trigger.")

    return " ".join(parts)

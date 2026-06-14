"""
ascend Feature 1 — Explainable Counterfactual Reasoning
═══════════════════════════════════════════════════════════
Generates "what-if" explanations for each analyzer's risk contribution.

Example output:
  "If urgency indicators were absent, risk would reduce from 82 → 47."

Boundary: This module does NOT recalculate detection. It uses simple
arithmetic subtraction on the existing findings to produce explanations.
"""

from ascend import ascend_config


def generate_counterfactuals(risk_score: float, findings: list[dict]) -> list[dict]:
    """
    Generate counterfactual explanations for each analyzer category.

    Args:
        risk_score: The final risk score (0–100) from core engine.
        findings:   List of finding dicts, each with keys:
                    analyzer, indicator, score, evidence, explanation.

    Returns:
        List of counterfactual explanation dicts:
        [
            {
                "category": "urgency",
                "category_label": "Urgency Indicators",
                "original_score": 82.0,
                "hypothetical_score": 47.0,
                "delta": 35.0,
                "finding_count": 3,
                "narrative": "If urgency indicators were absent, ..."
            },
            ...
        ]
    """
    if not ascend_config.COUNTERFACTUAL_ENABLED:
        return []

    if not findings:
        return []

    # ── Group findings by analyzer category ──
    category_scores: dict[str, float] = {}
    category_counts: dict[str, int] = {}
    for f in findings:
        cat = f.get("analyzer", "unknown")
        category_scores[cat] = category_scores.get(cat, 0.0) + f.get("score", 0.0)
        category_counts[cat] = category_counts.get(cat, 0) + 1

    # ── Category display names ──
    LABEL_MAP = {
        "keyword": "Phishing Keywords",
        "url": "URL Indicators",
        "sender": "Sender Anomalies",
        "urgency": "Urgency Indicators",
        "structure": "Structural Patterns",
    }

    # ── Generate counterfactual for each category that contributed ──
    counterfactuals = []
    for cat, cat_score in sorted(category_scores.items(),
                                  key=lambda x: x[1], reverse=True):
        if cat_score <= 0:
            continue

        hypothetical = max(0.0, risk_score - cat_score)
        delta = round(cat_score, 1)
        label = LABEL_MAP.get(cat, cat.replace("_", " ").title())
        count = category_counts.get(cat, 0)

        # Build human-readable narrative
        if delta >= 20:
            impact = "significantly reduce"
        elif delta >= 10:
            impact = "moderately reduce"
        else:
            impact = "slightly reduce"

        narrative = (
            f"If {label.lower()} were absent, the risk score would "
            f"{impact} from {risk_score:.0f} → {hypothetical:.0f} "
            f"(−{delta} points from {count} finding{'s' if count != 1 else ''})."
        )

        counterfactuals.append({
            "category": cat,
            "category_label": label,
            "original_score": round(risk_score, 1),
            "hypothetical_score": round(hypothetical, 1),
            "delta": delta,
            "finding_count": count,
            "narrative": narrative,
        })

    return counterfactuals

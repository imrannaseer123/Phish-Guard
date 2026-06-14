"""
ascend Feature 7 — Interactive "What-If" Learning Mode
═════════════════════════════════════════════════════════
Provides a sandbox where users can experiment with rule weights
to understand how each analyzer contributes to the risk score.

Risk scores are recalculated IN-MEMORY ONLY using user-provided
weights. The core detection engine is NEVER called or modified.

Clearly labeled as "Educational Simulation" in all outputs.

Boundary: Uses existing findings from analysis_logs. Never
persists adjusted scores. Core engine untouched.
"""

import json
from ascend import ascend_config


def simulate_risk_score(
    findings: list[dict],
    custom_weights: dict[str, float],
    default_weights: dict[str, float],
) -> dict:
    """
    Recalculate risk score using custom weights (sandbox mode).

    Args:
        findings:        List of finding dicts from analysis history.
        custom_weights:  User-provided weights (e.g. {"keyword": 30, "url": 20, ...}).
        default_weights: Original weights from config.SCORE_WEIGHTS.

    Returns:
        {
            "mode": "Educational Simulation",
            "original_score": 72.0,
            "simulated_score": 58.0,
            "delta": -14.0,
            "original_weights": {...},
            "custom_weights": {...},
            "analyzer_breakdown": {
                "keyword": {
                    "original_contribution": 18.0,
                    "simulated_contribution": 21.6,
                    "original_weight": 25,
                    "custom_weight": 30,
                    "raw_ratio": 0.72,
                },
                ...
            },
            "explanation": "Increasing keyword weight... resulted in...",
        }
    """
    if not ascend_config.WHATIF_SANDBOX_ENABLED:
        return {"mode": "Educational Simulation", "error": "Feature disabled."}

    if not findings:
        return {"mode": "Educational Simulation", "error": "No findings to simulate."}

    # ── Calculate original score (as core engine would) ──
    original_by_cat: dict[str, float] = {}
    for f in findings:
        cat = f.get("analyzer", "unknown")
        original_by_cat[cat] = original_by_cat.get(cat, 0.0) + f.get("score", 0.0)

    original_total = min(sum(original_by_cat.values()), 100.0)

    # ── Calculate score ratios per analyzer ──
    # Each finding's score was originally capped by the default weight.
    # We compute the "raw ratio" = actual_score / default_weight
    # Then apply: simulated = raw_ratio × custom_weight

    analyzer_breakdown = {}
    simulated_total = 0.0

    for cat, actual_score in original_by_cat.items():
        default_w = default_weights.get(cat, 0)
        custom_w = custom_weights.get(cat, default_w)

        if default_w > 0:
            # Ratio of how much of the weight was "used"
            raw_ratio = min(actual_score / default_w, 1.0)
        else:
            raw_ratio = 0.0

        simulated_contribution = raw_ratio * custom_w

        analyzer_breakdown[cat] = {
            "original_contribution": round(actual_score, 1),
            "simulated_contribution": round(simulated_contribution, 1),
            "original_weight": default_w,
            "custom_weight": custom_w,
            "raw_ratio": round(raw_ratio, 3),
        }

        simulated_total += simulated_contribution

    simulated_total = min(simulated_total, 100.0)
    delta = round(simulated_total - original_total, 1)

    # ── Generate explanation ──
    explanation_parts = []
    for cat, bd in sorted(
        analyzer_breakdown.items(),
        key=lambda x: abs(x[1]["simulated_contribution"] - x[1]["original_contribution"]),
        reverse=True,
    ):
        diff = bd["simulated_contribution"] - bd["original_contribution"]
        if abs(diff) >= 1:
            direction = "increased" if diff > 0 else "decreased"
            explanation_parts.append(
                f"{cat.title()} contribution {direction} by {abs(diff):.1f} pts "
                f"(weight: {bd['original_weight']} → {bd['custom_weight']})"
            )

    if explanation_parts:
        explanation = "Simulation results: " + "; ".join(explanation_parts[:3]) + "."
    else:
        explanation = "No significant changes with the provided weights."

    return {
        "mode": "Educational Simulation",
        "original_score": round(original_total, 1),
        "simulated_score": round(simulated_total, 1),
        "delta": delta,
        "original_weights": default_weights,
        "custom_weights": custom_weights,
        "analyzer_breakdown": analyzer_breakdown,
        "explanation": explanation,
    }


def get_default_weights() -> dict:
    """Return the current default weights for the sandbox UI."""
    import config
    return dict(config.SCORE_WEIGHTS)

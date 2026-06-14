"""
ascend Feature 4 — Psychological Manipulation Analyzer
═════════════════════════════════════════════════════════
Detects emotional manipulation techniques in email text:
  • Fear — threats, consequences, intimidation
  • Urgency — time pressure, deadlines
  • Reward — prizes, financial lures
  • Authority — impersonation of power figures

Uses keyword groups with intensity scoring (1–3).

Boundary: Produces explanation-only output. Does NOT
inflate the core risk score. Displayed as a separate
section in the analysis report.
"""

from ascend import ascend_config


def analyze_manipulation(subject: str, body_text: str) -> dict:
    """
    Detect psychological manipulation patterns in email text.

    Args:
        subject:   Email subject line.
        body_text: Plain-text email body.

    Returns:
        {
            "enabled": True,
            "categories": {
                "fear": {
                    "label": "Fear & Intimidation",
                    "emoji": "😨",
                    "intensity": 7,      # Sum of matched keyword weights
                    "max_intensity": 3,   # Highest single keyword weight
                    "matches": ["account suspended", "legal action"],
                    "level": "High",      # "None" | "Low" | "Medium" | "High"
                },
                ...
            },
            "dominant_type": "fear",
            "overall_level": "High",
            "narrative": "This email primarily uses fear-based manipulation...",
        }
    """
    if not ascend_config.PSYCH_ANALYZER_ENABLED:
        return {"enabled": False, "categories": {}, "dominant_type": None,
                "overall_level": "None", "narrative": "Feature disabled."}

    combined = f"{subject} {body_text}".lower()

    LABELS = {
        "fear": ("Fear & Intimidation", "😨"),
        "urgency": ("Urgency & Time Pressure", "⏰"),
        "reward": ("Reward & Enticement", "🎁"),
        "authority": ("Authority & Impersonation", "👔"),
    }

    categories = {}
    max_category_intensity = 0
    dominant = None

    for cat_key, keywords in ascend_config.PSYCH_KEYWORDS.items():
        matches = []
        total_intensity = 0
        max_kw_intensity = 0

        for keyword, intensity in keywords.items():
            if keyword in combined:
                matches.append(keyword)
                total_intensity += intensity
                max_kw_intensity = max(max_kw_intensity, intensity)

        # Classify level based on total intensity
        if total_intensity == 0:
            level = "None"
        elif total_intensity <= 3:
            level = "Low"
        elif total_intensity <= 8:
            level = "Medium"
        else:
            level = "High"

        label, emoji = LABELS.get(cat_key, (cat_key.title(), "📌"))

        categories[cat_key] = {
            "label": label,
            "emoji": emoji,
            "intensity": total_intensity,
            "max_intensity": max_kw_intensity,
            "matches": matches,
            "level": level,
        }

        if total_intensity > max_category_intensity:
            max_category_intensity = total_intensity
            dominant = cat_key

    # ── Overall assessment ──
    total_all = sum(c["intensity"] for c in categories.values())
    if total_all == 0:
        overall = "None"
    elif total_all <= 5:
        overall = "Low"
    elif total_all <= 15:
        overall = "Medium"
    else:
        overall = "High"

    narrative = _generate_narrative(categories, dominant, overall)

    return {
        "enabled": True,
        "categories": categories,
        "dominant_type": dominant,
        "overall_level": overall,
        "narrative": narrative,
    }


def _generate_narrative(
    categories: dict, dominant: str | None, overall: str
) -> str:
    """Generate a human-readable narrative of the manipulation analysis."""
    if overall == "None":
        return (
            "No significant psychological manipulation patterns detected. "
            "The email does not appear to use emotional pressure tactics."
        )

    active = [
        (k, v) for k, v in categories.items()
        if v["intensity"] > 0
    ]
    active.sort(key=lambda x: x[1]["intensity"], reverse=True)

    parts = []
    for cat_key, cat_data in active[:3]:  # Top 3 categories
        label = cat_data["label"]
        match_count = len(cat_data["matches"])
        top_kw = cat_data["matches"][:2]
        parts.append(
            f"{label} ({match_count} indicator{'s' if match_count != 1 else ''}: "
            f"'{', '.join(top_kw)}')"
        )

    if dominant:
        dom_label = categories[dominant]["label"]
        intro = f"This email primarily employs {dom_label.lower()} tactics. "
    else:
        intro = "This email uses mixed manipulation tactics. "

    return (
        intro
        + f"Overall manipulation level: {overall}. "
        + f"Detected patterns: {'; '.join(parts)}. "
        + "These patterns are commonly used in phishing to bypass rational decision-making."
    )

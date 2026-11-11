"""
Phishing Severity Index (PSI) Module (Feature 7)
─────────────────────────────────────────────────
Computes a composite Phishing Severity Index that considers:

    - Risk Score (40% weight) — raw detection score from analyzers
    - Intent Severity (30% weight) — mapped severity of classified intent
    - Potential Impact (30% weight) — heuristic based on indicator types

The PSI is displayed SEPARATELY from the main risk score and
NEVER modifies it. It provides an additional dimension of threat
assessment focused on potential damage rather than detection confidence.

Formula:
    PSI = (risk_component * 0.4) + (intent_component * 0.3) + (impact_component * 0.3)

Scale: 0–10 (rounded to 1 decimal)
Labels: Minimal (0-2) | Low (2-4) | Moderate (4-6) | Severe (6-8) | Critical (8-10)

Design Constraints:
    - Displayed separately from main risk score
    - Never modifies existing scoring
    - Fail-safe: returns default PSI on error
    - No shared mutable state
"""


# ─── Intent Severity Mapping ─────────────────────────────────────────────────
#
# Maps phishing intent categories to severity ratings (0-10).
# Higher severity = greater potential damage if attack succeeds.

INTENT_SEVERITY = {
    "Credential Harvesting": 8.0,
    "Financial Fraud": 9.5,
    "Malware Delivery": 9.0,
    "Identity Theft": 8.5,
    "Legitimate": 0.0,
}

# ─── Indicator Impact Weights ────────────────────────────────────────────────
#
# Maps specific detection indicators to their potential impact score.
# Impact reflects the damage level if the user falls for the attack.

INDICATOR_IMPACT = {
    "credential_request": 9.0,     # Direct credential theft
    "anchor_mismatch": 7.5,        # Deceptive link leading to phishing page
    "shortened_url": 6.0,          # URL obfuscation → potential malware/phishing
    "ip_based_url": 7.0,           # Direct IP = likely malicious infrastructure
    "excessive_subdomains": 5.5,   # Domain obfuscation technique
    "brand_impersonation": 8.0,    # Impersonating trusted brand
    "free_email_corporate": 6.5,   # Sender credibility manipulation
    "urgency_phrase": 4.0,         # Social engineering pressure
    "suspicious_keyword": 3.5,     # Phishing language patterns
    "excessive_caps": 2.5,         # Emotional manipulation
    "excessive_punctuation": 2.0,  # Emotional manipulation
    "generic_greeting": 3.0,       # Impersonality / mass targeting
}

# ─── PSI Labels ──────────────────────────────────────────────────────────────

PSI_LABELS = [
    (2.0,  "Minimal",  "🟢", "Negligible threat potential"),
    (4.0,  "Low",      "🟡", "Minor threat with limited impact potential"),
    (6.0,  "Moderate", "🟠", "Notable threat requiring caution"),
    (8.0,  "Severe",   "🔴", "Significant threat with high damage potential"),
    (10.0, "Critical", "⚫", "Maximum severity — immediate risk of serious harm"),
]


def compute_psi(report):
    """
    Compute the Phishing Severity Index for an analyzed email.

    Parameters
    ----------
    report : RiskReport
        The complete analysis report from risk_scorer.

    Returns
    -------
    dict
        {
            "psi_score": float,       # 0-10
            "psi_label": str,         # e.g., "Moderate"
            "psi_icon": str,          # Color emoji
            "psi_description": str,   # Human-readable description
            "components": {
                "risk": {"score": float, "weight": float, "contribution": float},
                "intent": {"score": float, "weight": float, "contribution": float},
                "impact": {"score": float, "weight": float, "contribution": float},
            },
            "explanation": str,
        }
    """
    try:
        # 1. Risk component: normalize risk_score (0-100) to 0-10
        risk_normalized = min(10.0, report.risk_score / 10.0)

        # 2. Intent component: map intent to severity
        intent_score = INTENT_SEVERITY.get(report.intent, 0.0)

        # 3. Impact component: average impact of triggered indicators
        indicators = [f.indicator for f in report.findings]
        if indicators:
            impact_scores = [
                INDICATOR_IMPACT.get(ind, 2.0)
                for ind in indicators
            ]
            impact_score = min(10.0, sum(impact_scores) / len(impact_scores))
        else:
            impact_score = 0.0

        # Compute weighted PSI
        risk_contribution = risk_normalized * 0.4
        intent_contribution = intent_score * 0.3
        impact_contribution = impact_score * 0.3

        psi_score = round(
            risk_contribution + intent_contribution + impact_contribution, 1
        )
        psi_score = min(10.0, max(0.0, psi_score))

        # Determine label
        psi_label, psi_icon, psi_description = _get_psi_label(psi_score)

        # Generate explanation
        explanation = _generate_psi_explanation(
            psi_score, psi_label, risk_normalized, intent_score,
            impact_score, report.intent, indicators
        )

        return {
            "psi_score": psi_score,
            "psi_label": psi_label,
            "psi_icon": psi_icon,
            "psi_description": psi_description,
            "components": {
                "risk": {
                    "score": round(risk_normalized, 1),
                    "weight": 0.4,
                    "contribution": round(risk_contribution, 2),
                },
                "intent": {
                    "score": round(intent_score, 1),
                    "weight": 0.3,
                    "contribution": round(intent_contribution, 2),
                },
                "impact": {
                    "score": round(impact_score, 1),
                    "weight": 0.3,
                    "contribution": round(impact_contribution, 2),
                },
            },
            "explanation": explanation,
        }

    except Exception:
        return _empty_psi()


def _get_psi_label(score):
    """Map PSI score to label, icon, and description."""
    for threshold, label, icon, description in PSI_LABELS:
        if score <= threshold:
            return label, icon, description
    return "Critical", "⚫", "Maximum severity"


def _generate_psi_explanation(psi_score, psi_label, risk_norm,
                               intent_score, impact_score,
                               intent_name, indicators):
    """Generate a human-readable explanation of the PSI components."""
    if psi_score <= 2.0:
        return (
            f"The Phishing Severity Index is {psi_score}/10 ({psi_label}). "
            f"This email poses negligible threat. The intent is classified as "
            f"'{intent_name}' with minimal impact potential."
        )

    parts = []
    if risk_norm >= 5.0:
        parts.append(f"high detection score ({risk_norm:.0f}/10)")
    if intent_score >= 7.0:
        parts.append(f"severe intent: {intent_name}")
    if impact_score >= 5.0:
        parts.append(f"significant potential impact ({impact_score:.1f}/10)")

    if parts:
        factors = ", ".join(parts)
        return (
            f"PSI is {psi_score}/10 ({psi_label}), driven by: {factors}. "
            f"This index reflects the potential severity of harm if the "
            f"attack were to succeed, independent of detection confidence."
        )

    return (
        f"PSI is {psi_score}/10 ({psi_label}). Component scores: "
        f"risk={risk_norm:.1f}, intent={intent_score:.1f}, "
        f"impact={impact_score:.1f}."
    )


def _empty_psi():
    """Return an empty/default PSI result."""
    return {
        "psi_score": 0.0,
        "psi_label": "Unknown",
        "psi_icon": "⚪",
        "psi_description": "PSI computation unavailable.",
        "components": {
            "risk": {"score": 0, "weight": 0.4, "contribution": 0},
            "intent": {"score": 0, "weight": 0.3, "contribution": 0},
            "impact": {"score": 0, "weight": 0.3, "contribution": 0},
        },
        "explanation": "Phishing Severity Index could not be computed.",
    }

"""
Phishing Kill-Chain Mapping Module (Feature 1)
───────────────────────────────────────────────
Maps detected analyzer findings to phishing lifecycle stages:

    Recon → Delivery → Exploitation → Credential Harvest → Monetization

This module consumes the existing Finding and RiskReport data structures
without modifying them. It uses indicator types and evidence text to
determine which kill-chain phases are active for a given email.

Academic Reference:
    Based on the Lockheed Martin Cyber Kill Chain framework adapted
    for email-based phishing attack classification.

Design Constraints:
    - Uses existing analyzer signals ONLY (no new detection logic)
    - No scoring changes — output is purely explanatory
    - Fail-safe: returns empty/default data on any error
    - No shared mutable state with core analyzer
"""

# ─── Kill-Chain Stage Definitions ─────────────────────────────────────────────
#
# Each stage maps to a set of indicators and evidence keywords that
# suggest the phishing email is operating at that lifecycle phase.

KILLCHAIN_STAGES = [
    {
        "id": "recon",
        "label": "🔍 Reconnaissance",
        "description": "Attacker gathers information about the target organization or individual.",
        "indicators": ["generic_greeting", "brand_impersonation"],
        "evidence_keywords": ["dear customer", "dear user", "dear sir", "account holder"],
        "explanation": "Generic greetings and brand impersonation suggest the attacker "
                       "is casting a wide net without specific target knowledge.",
    },
    {
        "id": "delivery",
        "label": "📨 Delivery",
        "description": "Phishing email is delivered to the target's inbox.",
        "indicators": ["shortened_url", "ip_based_url", "excessive_subdomains",
                        "free_email_corporate"],
        "evidence_keywords": ["bit.ly", "tinyurl", "click here", "click the link",
                              "click immediately"],
        "explanation": "Obfuscated URLs, shortened links, and suspicious sender domains "
                       "indicate the delivery mechanism of the phishing attack.",
    },
    {
        "id": "exploitation",
        "label": "⚡ Exploitation",
        "description": "Email attempts to exploit the recipient's trust or emotions.",
        "indicators": ["urgency_phrase", "excessive_caps", "excessive_punctuation",
                        "suspicious_keyword"],
        "evidence_keywords": ["urgent", "immediately", "act now", "suspended",
                              "compromised", "unauthorized", "final notice",
                              "legal action", "criminal"],
        "explanation": "Urgency tactics, emotional manipulation, and fear-inducing "
                       "language are exploitation techniques to bypass rational thinking.",
    },
    {
        "id": "credential_harvest",
        "label": "🎣 Credential Harvest",
        "description": "Email attempts to steal credentials or sensitive information.",
        "indicators": ["credential_request", "anchor_mismatch"],
        "evidence_keywords": ["password", "username", "login", "verify your account",
                              "confirm your identity", "update your information",
                              "reset your password", "sign in", "ssn", "credit card",
                              "bank account"],
        "explanation": "Requests for credentials, login pages, or sensitive information "
                       "indicate the email is attempting to harvest user data.",
    },
    {
        "id": "monetization",
        "label": "💰 Monetization",
        "description": "Attack aims to extract financial value from the victim.",
        "indicators": [],
        "evidence_keywords": ["wire transfer", "bank transfer", "payment", "invoice",
                              "tax refund", "prize", "lottery", "inheritance",
                              "unclaimed funds", "bitcoin", "cryptocurrency",
                              "western union", "money gram"],
        "explanation": "Financial lures and payment requests indicate the attacker "
                       "is attempting direct monetary extraction.",
    },
]


def map_to_killchain(findings, report=None):
    """
    Map a list of Finding objects to phishing kill-chain stages.

    Parameters
    ----------
    findings : list[Finding]
        The findings from the phishing engine analysis.
    report : RiskReport, optional
        The complete risk report (used for intent classification).

    Returns
    -------
    dict
        {
            "stages": [
                {"id": str, "label": str, "description": str,
                 "active": bool, "confidence": str, "explanation": str,
                 "matched_signals": list[str]},
                ...
            ],
            "primary_phase": str,    # Label of the most advanced active stage
            "phase_summary": str,    # Human-readable summary
            "active_count": int,     # Number of active stages
        }
    """
    try:
        # Collect all indicators and evidence from findings
        indicators = set(f.indicator for f in findings)
        evidence_text = " ".join(f.evidence.lower() for f in findings)

        stages_result = []
        active_stages = []

        for stage in KILLCHAIN_STAGES:
            # Check indicator matches
            matched_indicators = [
                ind for ind in stage["indicators"] if ind in indicators
            ]

            # Check evidence keyword matches
            matched_keywords = [
                kw for kw in stage["evidence_keywords"]
                if kw in evidence_text
            ]

            # Determine if this stage is active
            is_active = bool(matched_indicators or matched_keywords)

            # Compute confidence level based on match density
            total_matches = len(matched_indicators) + len(matched_keywords)
            if total_matches >= 3:
                confidence = "high"
            elif total_matches >= 1:
                confidence = "medium"
            else:
                confidence = "none"

            # Collect matched signal descriptions
            matched_signals = (
                [f"Indicator: {ind}" for ind in matched_indicators] +
                [f"Keyword: \"{kw}\"" for kw in matched_keywords]
            )

            stages_result.append({
                "id": stage["id"],
                "label": stage["label"],
                "description": stage["description"],
                "active": is_active,
                "confidence": confidence,
                "explanation": stage["explanation"] if is_active else "",
                "matched_signals": matched_signals,
            })

            if is_active:
                active_stages.append(stage)

        # Determine primary phase (most advanced active stage)
        if active_stages:
            primary = active_stages[-1]  # Last = most advanced in chain
            primary_phase = primary["label"]
        else:
            primary_phase = "No Active Phase"

        # Generate summary
        phase_summary = _generate_phase_summary(active_stages, report)

        return {
            "stages": stages_result,
            "primary_phase": primary_phase,
            "phase_summary": phase_summary,
            "active_count": len(active_stages),
        }

    except Exception:
        # Fail-safe: return empty/default structure
        return {
            "stages": [],
            "primary_phase": "Unknown",
            "phase_summary": "Kill-chain analysis unavailable.",
            "active_count": 0,
        }


def _generate_phase_summary(active_stages, report=None):
    """
    Generate a human-readable summary of the kill-chain analysis.

    The summary explains which phases are active and what this means
    for the overall threat assessment.
    """
    if not active_stages:
        return (
            "This email does not exhibit clear indicators of any phishing "
            "kill-chain stages. This suggests it is likely legitimate or "
            "uses techniques not covered by the current detection rules."
        )

    stage_names = [s["label"] for s in active_stages]
    count = len(active_stages)

    if count == 1:
        return (
            f"This email shows signals consistent with the "
            f"{stage_names[0]} phase of the phishing kill-chain. "
            f"This is an early-stage indicator that warrants caution."
        )

    if count >= 4:
        return (
            f"⚠️ This email activates {count} out of 5 kill-chain phases "
            f"({', '.join(stage_names)}), indicating a sophisticated, "
            f"multi-stage phishing attack. Exercise extreme caution."
        )

    return (
        f"This email activates {count} kill-chain phases: "
        f"{', '.join(stage_names)}. Multiple active phases suggest "
        f"a coordinated phishing attempt with clear attack progression."
    )
""",
<parameter name="EmptyFile">false

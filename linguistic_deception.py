"""
Linguistic Deception Analysis Module (Feature 2)
─────────────────────────────────────────────────
Analyzes email text for linguistic manipulation patterns:

    1. Emotional Manipulation — fear, greed, and urgency word clusters
    2. Pronoun Inconsistency — switching between we/I/they perspectives
    3. Tone Mismatch — formal greeting paired with informal body

This module complements the existing keyword analyzer by adding a
deeper linguistic layer. Results appear ONLY in the explanation layer
and do NOT modify the risk score.

Academic Reference:
    Draws from research on social engineering linguistics and deception
    detection in written communication (Hancock et al., 2007; Zhou et al., 2004).

Design Constraints:
    - Read-only analysis of email text
    - No scoring changes — output is explanatory only
    - No external NLP dependencies (uses regex + heuristics)
    - Fail-safe: returns empty results on any error
"""

import re


# ─── Emotional Manipulation Lexicons ──────────────────────────────────────────
#
# Categorized word clusters that indicate emotional manipulation.
# Each category has words/phrases and an explanation template.

EMOTION_CLUSTERS = {
    "fear": {
        "phrases": [
            "your account will be", "has been compromised", "unauthorized access",
            "security breach", "suspicious activity", "locked out",
            "will be terminated", "permanently deleted", "legal consequences",
            "law enforcement", "criminal investigation", "identity theft",
            "fraudulent activity", "we detected unusual", "compromised",
        ],
        "label": "😨 Fear Induction",
        "description": "Uses fear-inducing language to create panic and bypass "
                       "rational decision-making.",
    },
    "greed": {
        "phrases": [
            "you have won", "congratulations", "claim your prize",
            "lottery winner", "million dollars", "inheritance",
            "unclaimed funds", "free gift", "exclusive offer",
            "limited time offer", "special promotion", "cash reward",
            "you've been selected", "guaranteed income",
        ],
        "label": "🤑 Greed Exploitation",
        "description": "Exploits desire for financial gain or rewards to "
                       "lower the recipient's guard.",
    },
    "authority": {
        "phrases": [
            "we are required by law", "compliance department",
            "internal revenue service", "irs", "federal",
            "government agency", "official notification",
            "mandatory update", "regulatory requirement",
            "failure to comply", "your cooperation is required",
        ],
        "label": "👔 Authority Impersonation",
        "description": "Impersonates authority figures or institutions to "
                       "compel obedience without question.",
    },
    "scarcity": {
        "phrases": [
            "limited time", "expires today", "only today",
            "last chance", "final notice", "act now or",
            "offer expires", "deadline approaching", "time sensitive",
            "while supplies last", "exclusive access",
        ],
        "label": "⏳ Scarcity Pressure",
        "description": "Creates artificial time pressure to prevent careful "
                       "evaluation of the request.",
    },
}

# ─── Pronoun Analysis ─────────────────────────────────────────────────────────
#
# Legitimate business emails maintain consistent perspective.
# Phishing emails often switch between "we" (impersonating company)
# and "I" (personal tone) inconsistently.

PRONOUN_GROUPS = {
    "first_singular": re.compile(r"\b(i|me|my|myself|mine)\b", re.IGNORECASE),
    "first_plural": re.compile(r"\b(we|us|our|ourselves|ours)\b", re.IGNORECASE),
    "second": re.compile(r"\b(you|your|yours|yourself)\b", re.IGNORECASE),
    "third": re.compile(r"\b(they|them|their|theirs|he|she|his|her)\b", re.IGNORECASE),
}

# ─── Tone Indicators ─────────────────────────────────────────────────────────

FORMAL_GREETINGS = [
    "dear sir", "dear madam", "dear customer", "dear valued",
    "dear account holder", "dear user", "dear client",
    "to whom it may concern", "respected",
]

INFORMAL_INDICATORS = [
    "hey", "hi there", "what's up", "asap", "gonna", "wanna",
    "gotta", "lol", "omg", "btw", "fyi", "thx", "pls",
    "!!!", "???", "...", "click here now", "hurry up",
]


def analyze_linguistic_deception(subject, body_text):
    """
    Analyze email text for linguistic deception patterns.

    Parameters
    ----------
    subject : str
        Email subject line.
    body_text : str
        Plain-text email body.

    Returns
    -------
    dict
        {
            "emotional_manipulation": [
                {"category": str, "label": str, "description": str,
                 "matched_phrases": list[str], "intensity": str},
                ...
            ],
            "pronoun_analysis": {
                "inconsistency_detected": bool,
                "explanation": str,
                "distribution": dict[str, int],
            },
            "tone_mismatch": {
                "detected": bool,
                "explanation": str,
                "formal_signals": list[str],
                "informal_signals": list[str],
            },
            "deception_signals_count": int,
            "summary": str,
        }
    """
    try:
        full_text = f"{subject} {body_text}".lower() if (subject or body_text) else ""
        if not full_text.strip():
            return _empty_result()

        emotional = _analyze_emotional_manipulation(full_text)
        pronouns = _analyze_pronoun_consistency(body_text or "")
        tone = _analyze_tone_mismatch(full_text)

        # Count total deception signals
        signals_count = (
            len(emotional) +
            (1 if pronouns["inconsistency_detected"] else 0) +
            (1 if tone["detected"] else 0)
        )

        summary = _generate_summary(emotional, pronouns, tone, signals_count)

        return {
            "emotional_manipulation": emotional,
            "pronoun_analysis": pronouns,
            "tone_mismatch": tone,
            "deception_signals_count": signals_count,
            "summary": summary,
        }

    except Exception:
        return _empty_result()


def _analyze_emotional_manipulation(text):
    """Detect emotional manipulation word clusters in the text."""
    results = []

    for category, data in EMOTION_CLUSTERS.items():
        matched = [p for p in data["phrases"] if p in text]
        if matched:
            # Intensity based on match count
            if len(matched) >= 3:
                intensity = "high"
            elif len(matched) >= 2:
                intensity = "medium"
            else:
                intensity = "low"

            results.append({
                "category": category,
                "label": data["label"],
                "description": data["description"],
                "matched_phrases": matched,
                "intensity": intensity,
            })

    return results


def _analyze_pronoun_consistency(body_text):
    """
    Detect pronoun inconsistency patterns.

    Legitimate emails from companies typically use consistent "we/our"
    perspective. Phishing emails often mix perspectives inconsistently.
    """
    distribution = {}
    for group_name, pattern in PRONOUN_GROUPS.items():
        matches = pattern.findall(body_text.lower())
        distribution[group_name] = len(matches)

    # Check for inconsistency: significant use of both first-singular and first-plural
    first_singular = distribution.get("first_singular", 0)
    first_plural = distribution.get("first_plural", 0)

    inconsistency = (first_singular >= 2 and first_plural >= 2)

    if inconsistency:
        explanation = (
            f"The email switches between first-person singular ('I/me' used "
            f"{first_singular}×) and plural ('we/our' used {first_plural}×). "
            f"Legitimate corporate emails maintain consistent perspective. "
            f"This inconsistency may indicate a hastily crafted phishing email."
        )
    else:
        explanation = "Pronoun usage appears consistent."

    return {
        "inconsistency_detected": inconsistency,
        "explanation": explanation,
        "distribution": distribution,
    }


def _analyze_tone_mismatch(text):
    """
    Detect mismatch between formal greetings and informal body language.

    Phishing emails often start with overly formal greetings (to appear
    legitimate) but contain informal or aggressive language in the body.
    """
    formal_found = [g for g in FORMAL_GREETINGS if g in text]
    informal_found = [i for i in INFORMAL_INDICATORS if i in text]

    # Tone mismatch = formal greeting + informal body signals
    detected = bool(formal_found) and bool(informal_found)

    if detected:
        explanation = (
            f"The email uses formal greeting(s) ({', '.join(formal_found[:2])}) "
            f"but contains informal language ({', '.join(informal_found[:3])}). "
            f"This mismatch is common in phishing emails that try to appear "
            f"professional but reveal their true nature in the body."
        )
    else:
        explanation = "Tone is consistent throughout the email."

    return {
        "detected": detected,
        "explanation": explanation,
        "formal_signals": formal_found,
        "informal_signals": informal_found,
    }


def _generate_summary(emotional, pronouns, tone, signals_count):
    """Generate a human-readable summary of the linguistic analysis."""
    if signals_count == 0:
        return (
            "No significant linguistic deception patterns detected. "
            "The email's language appears natural and consistent."
        )

    parts = []
    if emotional:
        categories = [e["label"] for e in emotional]
        parts.append(f"emotional manipulation ({', '.join(categories)})")
    if pronouns["inconsistency_detected"]:
        parts.append("pronoun inconsistency")
    if tone["detected"]:
        parts.append("tone mismatch")

    joined = ", ".join(parts)

    if signals_count >= 3:
        return (
            f"⚠️ Multiple linguistic deception patterns detected: {joined}. "
            f"This combination of manipulation techniques strongly suggests "
            f"a social engineering attempt."
        )

    return (
        f"Linguistic analysis detected: {joined}. "
        f"These patterns are associated with social engineering but "
        f"should be considered alongside other risk indicators."
    )


def _empty_result():
    """Return an empty result structure for fail-safe handling."""
    return {
        "emotional_manipulation": [],
        "pronoun_analysis": {
            "inconsistency_detected": False,
            "explanation": "Analysis unavailable.",
            "distribution": {},
        },
        "tone_mismatch": {
            "detected": False,
            "explanation": "Analysis unavailable.",
            "formal_signals": [],
            "informal_signals": [],
        },
        "deception_signals_count": 0,
        "summary": "Linguistic deception analysis unavailable.",
    }
"""

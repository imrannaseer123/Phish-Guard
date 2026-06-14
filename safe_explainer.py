"""
Explainable False-Positive Reasoning Module (Feature 5)
───────────────────────────────────────────────────────
When an email is classified as "Low" risk, this module generates
explicit explanations of WHY it is considered safe.

Approach:
    1. Check for absence of each risk indicator category
    2. Identify positive trust signals (legitimate domain, proper greeting)
    3. Note low analyzer activation
    4. Compile into a human-readable list of safety reasons

This addresses the "explanation gap" where low-risk emails receive
minimal explanation. Users deserve to understand why an email is
considered safe, not just why it might be dangerous.

Academic Reference:
    Inspired by counterfactual explanation methods in XAI (Wachter et al., 2017)
    — explaining outcomes by highlighting what did NOT trigger.

Design Constraints:
    - Only activates when risk_level == "Low"
    - Read-only analysis of existing findings/report
    - No scoring changes
    - Fail-safe: returns empty list on error
"""

import config


# ─── Known Legitimate Domains ─────────────────────────────────────────────────
#
# Domains that are generally considered trustworthy. This list is used
# to provide positive trust signals, not to whitelist or bypass analysis.

TRUSTED_DOMAINS = [
    "google.com", "gmail.com", "microsoft.com", "outlook.com",
    "apple.com", "icloud.com", "amazon.com", "linkedin.com",
    "github.com", "slack.com", "zoom.us", "dropbox.com",
    "salesforce.com", "adobe.com", "notion.so", "figma.com",
    "stripe.com", "atlassian.com", "jira.com", "confluence.com",
    "stackoverflow.com", "npmjs.com", "pypi.org", "docker.com",
]


def explain_safe_classification(report, sender_domain=""):
    """
    Generate explanations for why an email is classified as safe.

    Parameters
    ----------
    report : RiskReport
        The complete analysis report from risk_scorer.
    sender_domain : str
        The domain of the email sender.

    Returns
    -------
    dict
        {
            "is_applicable": bool,       # True only if risk_level == "Low"
            "trust_signals": [
                {"icon": str, "title": str, "explanation": str},
                ...
            ],
            "absent_risks": [
                {"icon": str, "title": str, "explanation": str},
                ...
            ],
            "summary": str,
        }
    """
    try:
        # Only generate for low-risk emails
        if report.risk_level != "Low":
            return {"is_applicable": False, "trust_signals": [],
                    "absent_risks": [], "summary": ""}

        trust_signals = _identify_trust_signals(report, sender_domain)
        absent_risks = _identify_absent_risks(report)

        total_signals = len(trust_signals) + len(absent_risks)
        summary = _generate_safety_summary(trust_signals, absent_risks,
                                            report, sender_domain)

        return {
            "is_applicable": True,
            "trust_signals": trust_signals,
            "absent_risks": absent_risks,
            "summary": summary,
        }

    except Exception:
        return {"is_applicable": False, "trust_signals": [],
                "absent_risks": [], "summary": ""}


def _identify_trust_signals(report, sender_domain):
    """
    Identify positive indicators that suggest the email is legitimate.
    """
    signals = []
    indicators = set(f.indicator for f in report.findings)

    # 1. Low risk score
    if report.risk_score <= 10:
        signals.append({
            "icon": "✅",
            "title": "Very Low Risk Score",
            "explanation": (
                f"The email scored only {report.risk_score}/100, well below "
                f"the risk threshold of {config.RISK_LOW_MAX}. This indicates "
                f"minimal suspicious content detected by all five analyzers."
            ),
        })

    # 2. Legitimate sender domain
    if sender_domain and sender_domain.lower() in TRUSTED_DOMAINS:
        signals.append({
            "icon": "🏢",
            "title": "Recognized Sender Domain",
            "explanation": (
                f"The sender's domain ({sender_domain}) is a well-known, "
                f"legitimate service provider. While spoofing is possible, "
                f"this domain is generally trustworthy."
            ),
        })

    # 3. No brand impersonation
    if "brand_impersonation" not in indicators and "free_email_corporate" not in indicators:
        signals.append({
            "icon": "👤",
            "title": "Consistent Sender Identity",
            "explanation": (
                "The sender's display name is consistent with their email "
                "domain. No brand impersonation patterns were detected."
            ),
        })

    # 4. Legitimate intent classification
    if report.intent == "Legitimate":
        signals.append({
            "icon": "🎯",
            "title": "Legitimate Intent Classification",
            "explanation": (
                "The intent classifier determined this email's purpose "
                "is legitimate based on the absence of phishing-associated "
                "patterns and keywords."
            ),
        })

    # 5. Few or no findings
    if len(report.findings) <= 1:
        signals.append({
            "icon": "🔍",
            "title": "Minimal Detection Triggers",
            "explanation": (
                f"Only {len(report.findings)} detection rule(s) triggered, "
                f"indicating the email lacks typical phishing characteristics."
            ),
        })

    return signals


def _identify_absent_risks(report):
    """
    Identify risk categories that were NOT triggered, explaining
    their absence as a positive signal.
    """
    absent = []
    indicators = set(f.indicator for f in report.findings)
    active_analyzers = set(f.analyzer for f in report.findings)

    # Check each analyzer category for absence
    if "keyword" not in active_analyzers:
        absent.append({
            "icon": "🔤",
            "title": "No Suspicious Keywords Found",
            "explanation": (
                "The email does not contain common phishing keywords such as "
                "'verify your account', 'click here', or 'act immediately'. "
                "Phishing emails typically rely heavily on such phrases."
            ),
        })

    if "url" not in active_analyzers:
        absent.append({
            "icon": "🔗",
            "title": "No Suspicious URLs Detected",
            "explanation": (
                "No shortened links, IP-based URLs, excessive subdomains, "
                "or anchor-text mismatches were found. The email's links "
                "(if any) appear legitimate."
            ),
        })

    if "urgency" not in active_analyzers:
        absent.append({
            "icon": "⏰",
            "title": "No Urgency Tactics",
            "explanation": (
                "The email does not use high-pressure language, "
                "excessive capitalization, or aggressive punctuation. "
                "Legitimate emails rarely create artificial urgency."
            ),
        })

    if "credential_request" not in indicators:
        absent.append({
            "icon": "🔑",
            "title": "No Credential Requests",
            "explanation": (
                "The email does not ask for passwords, usernames, "
                "financial details, or other sensitive information. "
                "This is consistent with legitimate communication."
            ),
        })

    if "generic_greeting" not in indicators:
        absent.append({
            "icon": "👋",
            "title": "Personalized Greeting",
            "explanation": (
                "The email does not use generic greetings like "
                "'Dear Customer' or 'Dear Sir/Madam'. Personalized "
                "addressing is more common in legitimate emails."
            ),
        })

    return absent


def _generate_safety_summary(trust_signals, absent_risks, report, domain):
    """Generate a comprehensive summary explaining the safe classification."""
    total = len(trust_signals) + len(absent_risks)

    if total >= 6:
        return (
            f"This email has strong indicators of legitimacy. "
            f"{len(trust_signals)} positive trust signal(s) and "
            f"{len(absent_risks)} absent risk category(ies) confirm "
            f"it is very likely safe. Standard email hygiene still applies."
        )

    if total >= 3:
        return (
            f"Multiple factors support this email's safe classification: "
            f"low risk score ({report.risk_score}/100), "
            f"no significant threat indicators, and consistent sender identity. "
            f"Always verify unexpected requests through official channels."
        )

    return (
        f"This email scored {report.risk_score}/100 (Low risk). "
        f"While no major threats were detected, maintain general "
        f"email safety awareness."
    )
"""

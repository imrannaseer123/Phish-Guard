"""
Risk Scoring & Intent Classification Module
────────────────────────────────────────────
Aggregates findings into a single risk score (0–100),
classifies risk level and phishing intent,
and generates a structured explainability report.
"""

from dataclasses import dataclass, field
from phishing_engine import Finding
import config


@dataclass
class RiskReport:
    """Complete explainability report for a single email analysis."""
    risk_score: float                    # 0–100
    risk_level: str                      # "Low" | "Medium" | "High"
    intent: str                          # Phishing intent category
    findings: list[Finding]              # All individual findings
    analyzer_scores: dict[str, float]    # Per-analyzer subtotals
    explanation_summary: str             # One-paragraph human summary
    awareness_tips: list[str]            # Actionable safety tips


def compute_risk_score(findings: list[Finding]) -> float:
    """Sum all finding scores, capped at 100."""
    total = sum(f.score for f in findings)
    return min(total, 100.0)


def classify_risk_level(score: float) -> str:
    """Map score to Low / Medium / High."""
    if score <= config.RISK_LOW_MAX:
        return "Low"
    elif score <= config.RISK_MEDIUM_MAX:
        return "Medium"
    else:
        return "High"


def compute_analyzer_scores(findings: list[Finding]) -> dict[str, float]:
    """Group and sum scores by analyzer name."""
    scores: dict[str, float] = {}
    for f in findings:
        scores[f.analyzer] = scores.get(f.analyzer, 0.0) + f.score
    return scores


def classify_intent(findings: list[Finding]) -> str:
    """
    Determine the most likely phishing intent based on findings.
    Uses indicator types as signals.
    """
    indicators = [f.indicator for f in findings]
    evidence_text = " ".join(f.evidence.lower() for f in findings)

    # Priority-ordered intent rules
    if "credential_request" in indicators or "password" in evidence_text:
        return "Credential Harvesting"

    if any(kw in evidence_text for kw in [
        "bank", "wire transfer", "payment", "invoice", "tax refund",
        "prize", "lottery", "inheritance", "unclaimed funds"
    ]):
        return "Financial Fraud"

    if any(kw in evidence_text for kw in [
        "attachment", "download", "open the attached", "enable macros"
    ]):
        return "Malware Delivery"

    if any(kw in evidence_text for kw in [
        "social security", "ssn", "date of birth", "mother's maiden"
    ]):
        return "Identity Theft"

    # If some risk exists but no specific intent
    total_score = sum(f.score for f in findings)
    if total_score > config.RISK_LOW_MAX:
        return "Credential Harvesting"  # Default high-risk intent

    return "Legitimate"


def generate_summary(risk_level: str, intent: str, analyzer_scores: dict) -> str:
    """Generate a one-paragraph human-readable summary."""
    if risk_level == "Low":
        return (
            "This email shows minimal signs of phishing. No significant "
            "suspicious indicators were detected. However, always remain "
            "cautious with unexpected emails and verify sender identity "
            "before clicking any links."
        )

    top_analyzers = sorted(analyzer_scores.items(), key=lambda x: x[1], reverse=True)
    top_names = [f"{name} analysis" for name, _ in top_analyzers[:3] if _ > 0]
    areas = ", ".join(top_names) if top_names else "multiple areas"

    if risk_level == "Medium":
        return (
            f"This email has moderate phishing risk. Suspicious signals were "
            f"detected in {areas}. The likely intent appears to be "
            f'"{intent}". Exercise caution — verify the sender through an '
            f"independent channel before taking any action."
        )

    return (
        f"⚠️ HIGH RISK: This email shows strong phishing characteristics. "
        f"Major red flags were found in {areas}. The detected intent is "
        f'"{intent}". Do NOT click any links, download attachments, or '
        f"provide any personal information. Report this email as phishing."
    )


def generate_awareness_tips(risk_level: str, findings: list[Finding]) -> list[str]:
    """Generate contextual safety tips based on the specific findings."""
    tips = []
    indicators = set(f.indicator for f in findings)

    if "shortened_url" in indicators or "ip_based_url" in indicators:
        tips.append(
            "🔗 Hover over links before clicking to see the actual destination URL. "
            "If it looks suspicious or unfamiliar, do not click."
        )

    if "brand_impersonation" in indicators or "free_email_corporate" in indicators:
        tips.append(
            "🏢 Verify the sender's email domain. Official companies send emails "
            "from their own domain, not from free email providers."
        )

    if "credential_request" in indicators:
        tips.append(
            "🔑 Never share passwords, PINs, or financial details via email. "
            "Legitimate organizations will never ask for this information by email."
        )

    if "urgency_phrase" in indicators or "excessive_caps" in indicators:
        tips.append(
            "⏰ Be wary of emails that create urgency or panic. Scammers use "
            "time pressure to prevent you from thinking critically."
        )

    if "anchor_mismatch" in indicators:
        tips.append(
            "🔍 The display text of a link may differ from its actual destination. "
            "Always check the actual URL in your browser's status bar before clicking."
        )

    if "generic_greeting" in indicators:
        tips.append(
            "👤 Phishing emails often use generic greetings like 'Dear Customer'. "
            "Real companies that you have accounts with typically address you by name."
        )

    # Always-on general tips
    tips.append(
        "🛡️ When in doubt, contact the company directly using their official "
        "website or phone number — never use contact info from a suspicious email."
    )

    if risk_level == "High":
        tips.append(
            "🚨 Report this email as phishing in your email client and delete it. "
            "Do not forward it to others."
        )

    return tips


def generate_report(findings: list[Finding]) -> RiskReport:
    """
    Master function: take all findings and produce a complete
    explainability report.
    """
    risk_score = compute_risk_score(findings)
    risk_level = classify_risk_level(risk_score)
    intent = classify_intent(findings)
    analyzer_scores = compute_analyzer_scores(findings)
    summary = generate_summary(risk_level, intent, analyzer_scores)
    tips = generate_awareness_tips(risk_level, findings)

    return RiskReport(
        risk_score=round(risk_score, 1),
        risk_level=risk_level,
        intent=intent,
        findings=findings,
        analyzer_scores=analyzer_scores,
        explanation_summary=summary,
        awareness_tips=tips,
    )

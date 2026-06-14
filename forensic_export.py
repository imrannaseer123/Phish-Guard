"""
Forensic Evidence Export Module (Feature 8)
───────────────────────────────────────────
Generates downloadable forensic reports in JSON format containing:

    - Extracted URLs and their risk indicators
    - All detection findings with scores
    - Sender metadata
    - Analysis timestamps
    - Risk and intent classification
    - Kill-chain stage mapping (if available)

Privacy Constraints:
    - No email body storage — only metadata and findings
    - No PII beyond sender address (already in analysis_logs)
    - Export is a point-in-time snapshot, not a persistent record

Output Format:
    JSON (no external dependencies required)

Design Constraints:
    - Read-only: exports existing analysis data
    - No new database tables
    - No external dependencies
    - Fail-safe: returns error JSON on failure
"""

import json
from datetime import datetime, timezone


def generate_forensic_report(email_msg, report, findings_serialized,
                              killchain_data=None, psi_data=None,
                              domain_data=None, linguistic_data=None):
    """
    Generate a comprehensive forensic evidence report.

    Parameters
    ----------
    email_msg : dict
        The email message metadata (subject, sender, date, id).
    report : RiskReport
        The analysis report from risk_scorer.
    findings_serialized : list[dict]
        Serialized findings from the analysis.
    killchain_data : dict, optional
        Kill-chain mapping results.
    psi_data : dict, optional
        Phishing Severity Index results.
    domain_data : dict, optional
        Domain heuristics results.
    linguistic_data : dict, optional
        Linguistic deception analysis results.

    Returns
    -------
    dict
        Complete forensic report ready for JSON serialization.
    """
    try:
        now = datetime.now(timezone.utc).isoformat()

        forensic = {
            # ── Report Metadata ───────────────────────────────────────
            "report_metadata": {
                "generated_at": now,
                "generator": "PhishGuard Forensic Export v2.0",
                "report_type": "Email Phishing Forensic Analysis",
                "disclaimer": (
                    "This report is generated for security analysis purposes "
                    "only. It does not contain email body content to preserve "
                    "privacy. Findings are based on heuristic analysis and "
                    "should be verified by a security professional."
                ),
            },

            # ── Email Metadata ────────────────────────────────────────
            "email_metadata": {
                "message_id": email_msg.get("id", ""),
                "subject": email_msg.get("subject", ""),
                "sender": email_msg.get("sender", ""),
                "date": email_msg.get("date", ""),
                "snippet": email_msg.get("snippet", "")[:100] + "..."
                           if email_msg.get("snippet") else "",
            },

            # ── Risk Assessment ───────────────────────────────────────
            "risk_assessment": {
                "risk_score": report.risk_score,
                "risk_level": report.risk_level,
                "intent_classification": report.intent,
                "explanation_summary": report.explanation_summary,
                "analyzer_scores": report.analyzer_scores,
            },

            # ── Detection Findings ────────────────────────────────────
            "detection_findings": {
                "total_findings": len(findings_serialized),
                "findings": findings_serialized,
                "findings_by_analyzer": _group_findings_by_analyzer(
                    findings_serialized
                ),
            },

            # ── URL Analysis ──────────────────────────────────────────
            "url_analysis": _extract_url_findings(findings_serialized),

            # ── Indicators of Compromise (IOCs) ──────────────────────
            "iocs": _extract_iocs(findings_serialized, email_msg),

            # ── Awareness Tips ────────────────────────────────────────
            "awareness_tips": report.awareness_tips,
        }

        # ── Optional Extension Data ──────────────────────────────────
        if killchain_data:
            forensic["killchain_analysis"] = {
                "primary_phase": killchain_data.get("primary_phase", ""),
                "active_stages": [
                    s for s in killchain_data.get("stages", [])
                    if s.get("active")
                ],
                "phase_summary": killchain_data.get("phase_summary", ""),
            }

        if psi_data:
            forensic["severity_index"] = {
                "psi_score": psi_data.get("psi_score", 0),
                "psi_label": psi_data.get("psi_label", ""),
                "components": psi_data.get("components", {}),
                "explanation": psi_data.get("explanation", ""),
            }

        if domain_data:
            forensic["domain_analysis"] = {
                "domain": domain_data.get("domain", ""),
                "risk_indicators": domain_data.get("risk_indicators", 0),
                "findings": domain_data.get("findings", []),
                "summary": domain_data.get("summary", ""),
            }

        if linguistic_data:
            forensic["linguistic_analysis"] = {
                "deception_signals": linguistic_data.get(
                    "deception_signals_count", 0
                ),
                "emotional_manipulation": linguistic_data.get(
                    "emotional_manipulation", []
                ),
                "summary": linguistic_data.get("summary", ""),
            }

        return forensic

    except Exception:
        return {
            "error": "Failed to generate forensic report",
            "generated_at": datetime.now(timezone.utc).isoformat(),
        }


def _group_findings_by_analyzer(findings):
    """Group findings by their analyzer category."""
    grouped = {}
    for f in findings:
        analyzer = f.get("analyzer", "unknown")
        if analyzer not in grouped:
            grouped[analyzer] = []
        grouped[analyzer].append(f)
    return grouped


def _extract_url_findings(findings):
    """Extract URL-related findings into a dedicated section."""
    url_findings = [
        f for f in findings
        if f.get("analyzer") == "url"
    ]

    urls = []
    for f in url_findings:
        urls.append({
            "indicator": f.get("indicator", ""),
            "evidence": f.get("evidence", ""),
            "risk_score": f.get("score", 0),
            "explanation": f.get("explanation", ""),
        })

    return {
        "total_suspicious_urls": len(urls),
        "urls": urls,
    }


def _extract_iocs(findings, email_msg):
    """
    Extract Indicators of Compromise (IOCs) from the analysis.

    IOCs are observable artifacts that indicate potential compromise.
    No email body content is included.
    """
    iocs = {
        "sender_address": email_msg.get("sender", ""),
        "suspicious_urls": [],
        "suspicious_indicators": [],
        "risk_keywords_detected": [],
    }

    for f in findings:
        indicator = f.get("indicator", "")
        evidence = f.get("evidence", "")

        if indicator in ("shortened_url", "ip_based_url",
                         "excessive_subdomains", "anchor_mismatch"):
            iocs["suspicious_urls"].append({
                "type": indicator,
                "value": evidence,
            })
        elif indicator in ("credential_request", "brand_impersonation"):
            iocs["suspicious_indicators"].append({
                "type": indicator,
                "evidence": evidence,
            })
        elif indicator == "suspicious_keyword":
            iocs["risk_keywords_detected"].append(evidence)

    return iocs


def format_report_json(forensic_data, indent=2):
    """
    Format the forensic report as a pretty-printed JSON string.

    Parameters
    ----------
    forensic_data : dict
        The forensic report dictionary.
    indent : int
        JSON indentation level.

    Returns
    -------
    str
        Pretty-printed JSON string.
    """
    try:
        return json.dumps(forensic_data, indent=indent, ensure_ascii=False,
                          default=str)
    except Exception:
        return json.dumps({"error": "Failed to serialize report"})

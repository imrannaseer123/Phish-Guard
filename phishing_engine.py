"""
Explainable Phishing Detection Engine
──────────────────────────────────────
Rule-based, transparent analyzers that evaluate email features
and return scored findings with human-readable explanations.

Each analyzer produces a list of Finding objects. No black-box logic.
"""

from dataclasses import dataclass, field
import re

import config
import preprocessor
import qr_analyzer
import ocr_analyzer
import header_forensics


@dataclass
class Finding:
    """A single scored observation with human-readable explanation."""
    analyzer: str            # Which analyzer produced this (e.g. "keyword")
    indicator: str           # Short name (e.g. "suspicious_keyword")
    score: float             # Points contributed to risk (positive = riskier)
    evidence: str            # The actual text/data that triggered the finding
    explanation: str         # Plain-English why this matters


@dataclass
class EmailData:
    """Structured email data ready for analysis."""
    subject: str = ""
    sender_raw: str = ""     # Original From header
    body_text: str = ""      # Plain-text body (HTML stripped)
    body_html: str = ""      # Raw HTML body (for anchor analysis)
    date: str = ""
    message_id: str = ""
    language: str = "en"
    translated_body: str = ""
    headers: dict = field(default_factory=dict)
    attachments: list = field(default_factory=list)

# ═══════════════════════════════════════════════════════════════════════════════
# ANALYZER 1: Keyword Analyzer (max 25 pts)
# ═══════════════════════════════════════════════════════════════════════════════

def analyze_keywords(email: EmailData) -> list[Finding]:
    """
    Scan subject + body for known phishing keywords/phrases.
    Each match adds points, capped at the weight limit.
    """
    findings = []
    combined = preprocessor.normalize_text(
        (email.subject or "") + " " + (email.body_text or "")
    )
    max_score = config.SCORE_WEIGHTS["keyword"]
    per_hit = 5.0
    total = 0.0

    for keyword in config.PHISHING_KEYWORDS:
        if keyword.lower() in combined and total < max_score:
            score = min(per_hit, max_score - total)
            findings.append(Finding(
                analyzer="keyword",
                indicator="suspicious_keyword",
                score=score,
                evidence=keyword,
                explanation=(
                    f'The phrase "{keyword}" is commonly used in phishing emails '
                    f"to manipulate recipients into taking unsafe actions."
                ),
            ))
            total += score

    return findings


# ═══════════════════════════════════════════════════════════════════════════════
# ANALYZER 2: URL Analyzer (max 25 pts)
# ═══════════════════════════════════════════════════════════════════════════════

def analyze_urls(email: EmailData) -> list[Finding]:
    """
    Examine URLs in the email for red flags:
    - Shortened links
    - IP-based URLs
    - Excessive subdomains
    - Anchor text ≠ href mismatch
    """
    findings = []
    max_score = config.SCORE_WEIGHTS["url"]
    total = 0.0

    # URLs from plain text
    text_urls = preprocessor.extract_urls(email.body_text)
    # URLs from HTML anchors (with display text)
    html_links = preprocessor.extract_urls_from_html(email.body_html)

    all_urls = list(set(text_urls + [link["href"] for link in html_links]))

    if not all_urls:
        return findings

    for url in all_urls:
        if total >= max_score:
            break

        # Shortened URL check
        if preprocessor.is_shortened_url(url):
            score = min(8.0, max_score - total)
            findings.append(Finding(
                analyzer="url",
                indicator="shortened_url",
                score=score,
                evidence=url,
                explanation=(
                    f"This URL uses a link-shortening service, which hides the "
                    f"true destination. Phishers use this to disguise malicious sites."
                ),
            ))
            total += score

        # IP-based URL check
        if preprocessor.is_ip_based_url(url):
            score = min(10.0, max_score - total)
            findings.append(Finding(
                analyzer="url",
                indicator="ip_based_url",
                score=score,
                evidence=url,
                explanation=(
                    f"This URL uses a raw IP address instead of a domain name. "
                    f"Legitimate services almost never use IP-based URLs in emails."
                ),
            ))
            total += score

        # Excessive subdomains
        sub_count = preprocessor.count_subdomains(url)
        if sub_count >= 3:
            score = min(5.0, max_score - total)
            findings.append(Finding(
                analyzer="url",
                indicator="excessive_subdomains",
                score=score,
                evidence=f"{url} ({sub_count} subdomains)",
                explanation=(
                    f"This URL has {sub_count} subdomains, which is unusual. "
                    f"Attackers use deep subdomains to mimic legitimate domains "
                    f"(e.g., login.secure.bank.attacker.com)."
                ),
            ))
            total += score

    # Anchor-text ≠ href mismatch
    for link in html_links:
        if total >= max_score:
            break
        display = link["display_text"].strip().lower()
        href = link["href"].strip().lower()
        # If display text looks like a URL but differs from the href
        if display.startswith(("http://", "https://", "www.")) and display != href:
            if href not in display and display not in href:
                score = min(10.0, max_score - total)
                findings.append(Finding(
                    analyzer="url",
                    indicator="anchor_mismatch",
                    score=score,
                    evidence=f'Display: "{link["display_text"]}" → Href: "{link["href"]}"',
                    explanation=(
                        f"The clickable text shows one URL but actually links to a "
                        f"different destination. This is a strong phishing indicator."
                    ),
                ))
                total += score

    # ─────────────────────────────────────────────────────────────────────────
    # External Threat Intelligence (Feature 6)
    # ─────────────────────────────────────────────────────────────────────────
    try:
        import threat_intel
        ti_results = threat_intel.batch_check_urls(all_urls)
        
        for match in ti_results:
            # Threat Intel is high confidence, so we allow it to boost score significantly
            # We treat it as a separate finding type but group under 'url' analyzer
            res_score = match['analysis']['score']
            
            # Map 0-100 TI score to 0-30 engine points
            engine_score = min(30.0, (res_score / 100) * 30)
            
            findings.append(Finding(
                analyzer="threat_intel",
                indicator="known_malicious_url",
                score=engine_score,
                evidence=f"{match['url']} ({match['analysis']['classification']})",
                explanation=(
                    f"External threat intelligence identified this URL as "
                    f"likely {match['analysis']['classification']} (Source: {match['analysis']['source']})."
                ),
            ))
    except ImportError:
        pass
    except Exception as e:
        print(f"Threat Intel check failed: {e}")

    return findings


# ═══════════════════════════════════════════════════════════════════════════════
# ANALYZER 3: Sender Analyzer (max 20 pts)
# ═══════════════════════════════════════════════════════════════════════════════

def analyze_sender(email: EmailData) -> list[Finding]:
    """
    Inspect the sender's identity:
    - Display-name vs. domain mismatch
    - Free email provider impersonating a brand
    - Reply-to mismatch patterns
    """
    findings = []
    max_score = config.SCORE_WEIGHTS["sender"]
    total = 0.0

    sender_info = preprocessor.parse_sender(email.sender_raw)
    display_name = sender_info["display_name"].lower()
    domain = sender_info["domain"].lower()

    if not domain:
        return findings

    # Display-name contains a well-known brand but domain doesn't match
    known_brands = [
        "paypal", "amazon", "apple", "microsoft", "google", "netflix",
        "facebook", "instagram", "linkedin", "twitter", "bank of america",
        "wells fargo", "chase", "citibank", "dropbox", "adobe",
    ]
    for brand in known_brands:
        if brand in display_name and brand not in domain:
            score = min(12.0, max_score - total)
            findings.append(Finding(
                analyzer="sender",
                indicator="brand_impersonation",
                score=score,
                evidence=f'Display name: "{sender_info["display_name"]}", Domain: {domain}',
                explanation=(
                    f'The sender displays as "{sender_info["display_name"]}" '
                    f'but the email domain is "{domain}", which does not belong to {brand.title()}. '
                    f"This is a common impersonation technique."
                ),
            ))
            total += score
            break

    # Free email provider for corporate-looking communications
    if domain in config.FREE_EMAIL_PROVIDERS and display_name:
        # Check if display name implies a company/organization
        corporate_words = ["inc", "ltd", "corp", "team", "support", "admin",
                           "service", "department", "official", "helpdesk"]
        for word in corporate_words:
            if word in display_name:
                score = min(8.0, max_score - total)
                findings.append(Finding(
                    analyzer="sender",
                    indicator="free_email_corporate",
                    score=score,
                    evidence=f'"{sender_info["display_name"]}" using {domain}',
                    explanation=(
                        f'The sender claims to be "{sender_info["display_name"]}" '
                        f"but uses a free email provider ({domain}). Legitimate "
                        f"organizations use their own domain for official emails."
                    ),
                ))
                total += score
                break

    return findings


# ═══════════════════════════════════════════════════════════════════════════════
# ANALYZER 4: Urgency / Threat Analyzer (max 15 pts)
# ═══════════════════════════════════════════════════════════════════════════════

def analyze_urgency(email: EmailData) -> list[Finding]:
    """
    Detect urgency/threat manipulation:
    - Urgent language
    - ALL CAPS
    - Excessive punctuation
    """
    findings = []
    max_score = config.SCORE_WEIGHTS["urgency"]
    total = 0.0

    combined = (email.subject or "") + " " + (email.body_text or "")
    combined_lower = combined.lower()

    # Urgency phrases
    per_hit = 4.0
    for phrase in config.URGENCY_PHRASES:
        if phrase in combined_lower and total < max_score:
            score = min(per_hit, max_score - total)
            findings.append(Finding(
                analyzer="urgency",
                indicator="urgency_phrase",
                score=score,
                evidence=phrase,
                explanation=(
                    f'The phrase "{phrase}" creates artificial time pressure. '
                    f"Phishers use urgency to rush victims into acting without thinking."
                ),
            ))
            total += score

    # ALL CAPS in subject
    if email.subject and preprocessor.has_excessive_caps(email.subject, 0.6):
        score = min(4.0, max_score - total)
        findings.append(Finding(
            analyzer="urgency",
            indicator="excessive_caps",
            score=score,
            evidence=email.subject,
            explanation=(
                f"The subject line uses excessive capital letters, which is a "
                f"common pressure tactic in phishing and spam emails."
            ),
        ))
        total += score

    # Excessive punctuation
    if preprocessor.has_excessive_punctuation(combined, 5):
        score = min(3.0, max_score - total)
        findings.append(Finding(
            analyzer="urgency",
            indicator="excessive_punctuation",
            score=score,
            evidence=f"Found {'!'*min(combined.count('!'), 10)} or {'?'*min(combined.count('?'), 10)}",
            explanation=(
                f"Excessive use of exclamation marks or question marks is a "
                f"psychological pressure technique commonly found in phishing emails."
            ),
        ))
        total += score

    return findings


# ═══════════════════════════════════════════════════════════════════════════════
# ANALYZER 5: Structure Analyzer (max 15 pts)
# ═══════════════════════════════════════════════════════════════════════════════

def analyze_structure(email: EmailData) -> list[Finding]:
    """
    Examine the email's structural patterns:
    - Generic greeting or no greeting
    - Requests for credentials/sensitive info
    - Grammar/spelling signals
    """
    findings = []
    max_score = config.SCORE_WEIGHTS["structure"]
    total = 0.0
    body_lower = (email.body_text or "").lower()

    # Generic greeting
    generic_greetings = [
        "dear customer", "dear valued customer", "dear user",
        "dear sir/madam", "dear account holder", "dear member",
        "dear client", "dear subscriber",
    ]
    for greeting in generic_greetings:
        if greeting in body_lower:
            score = min(5.0, max_score - total)
            findings.append(Finding(
                analyzer="structure",
                indicator="generic_greeting",
                score=score,
                evidence=greeting,
                explanation=(
                    f'The email uses a generic greeting ("{greeting}") instead of '
                    f"your actual name. Legitimate senders who have a relationship "
                    f"with you usually address you by name."
                ),
            ))
            total += score
            break

    # Requests for credentials
    for keyword in config.CREDENTIAL_KEYWORDS:
        if keyword in body_lower and total < max_score:
            score = min(6.0, max_score - total)
            findings.append(Finding(
                analyzer="structure",
                indicator="credential_request",
                score=score,
                evidence=keyword,
                explanation=(
                    f'The email references "{keyword}", which is sensitive '
                    f"information. Legitimate organizations never ask you to "
                    f"provide sensitive data via email."
                ),
            ))
            total += score
            break  # One is enough

    # No signature/sign-off (very short body)
    if len(body_lower.split()) < 20 and any(
        url_ind in body_lower for url_ind in ["click", "http", "link"]
    ):
        score = min(4.0, max_score - total)
        findings.append(Finding(
            analyzer="structure",
            indicator="minimal_body",
            score=score,
            evidence=f"Body has only {len(body_lower.split())} words with a link",
            explanation=(
                f"The email has very little text but contains a link. "
                f"Phishing emails are often short, urging you to click "
                f"without providing proper context."
            ),
        ))
        total += score

    return findings


# ═══════════════════════════════════════════════════════════════════════════════
# MASTER ANALYSIS FUNCTION
# ═══════════════════════════════════════════════════════════════════════════════

def analyze_email(email: EmailData) -> list[Finding]:
    """
    Run all analyzers against the email and return combined findings.
    This is the single entry point for the detection engine.
    """
    all_findings = []
    
    # ─── 0. Multilingual Support ─────────────────────────────────────────────
    # Detect language and translate if necessary
    try:
        import multilingual
        multilingual.analyze_language(email)
    except Exception as e:
        print(f"Multilingual analysis failed: {e}")

    # Use translated body for text analysis if available
    original_body = email.body_text
    if email.translated_body:
        email.body_text = email.translated_body

    # ─── 1. Keyword Analysis ─────────────────────────────────────────────────
    all_findings.extend(analyze_keywords(email))
    all_findings.extend(analyze_urls(email))
    all_findings.extend(analyze_sender(email))
    all_findings.extend(analyze_urgency(email))
    all_findings.extend(analyze_structure(email))
    
    # Restore original structure
    email.body_text = original_body
    
    # ─── 6. Headers & Forensics ──────────────────────────────────────────────
    all_findings.extend(header_forensics.analyze_headers(email))
    
    # Image Analysis (Additive)
    for attachment in email.attachments:
        mime = attachment.get("mime_type", "")
        fname = attachment.get("filename", "")
        data = attachment.get("data")
        
        if not data:
            continue
            
        # QR Codes & OCR (Check extensions and mime)
        if "image" in mime or fname.lower().endswith((".png", ".jpg", ".jpeg", ".bmp", ".gif")):
             # QR Analysis
             all_findings.extend(qr_analyzer.scan_qr_codes(data, fname))
             
             # OCR Analysis
             text = ocr_analyzer.extract_text_from_image(data, fname)
             all_findings.extend(ocr_analyzer.analyze_ocr_text(text, fname))

    return all_findings

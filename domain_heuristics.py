"""
Domain Infrastructure Heuristics Module (Feature 4)
────────────────────────────────────────────────────
Provides offline, heuristic-based domain analysis:

    1. Domain Age Indicators — character pattern analysis suggesting
       recently registered or disposable domains
    2. Registrar Pattern Flags — suspicious TLD detection
    3. Lookalike Detection — Levenshtein distance to well-known brands

All analysis is OFFLINE — no DNS lookups, WHOIS queries, or network
requests. Results are displayed as advisory evidence only and do NOT
alter the risk score.

Design Constraints:
    - Pure heuristic logic (no network I/O)
    - Advisory-only evidence panel
    - Fail-safe: returns empty results on error
    - No shared mutable state
"""

import re


# ─── Well-Known Brand Domains ─────────────────────────────────────────────────
#
# Used for lookalike detection. These represent brands commonly
# impersonated in phishing campaigns.

KNOWN_BRANDS = {
    "google.com": "Google",
    "microsoft.com": "Microsoft",
    "apple.com": "Apple",
    "amazon.com": "Amazon",
    "paypal.com": "PayPal",
    "facebook.com": "Facebook",
    "netflix.com": "Netflix",
    "linkedin.com": "LinkedIn",
    "twitter.com": "Twitter",
    "instagram.com": "Instagram",
    "dropbox.com": "Dropbox",
    "chase.com": "Chase Bank",
    "wellsfargo.com": "Wells Fargo",
    "bankofamerica.com": "Bank of America",
    "citibank.com": "Citibank",
    "usps.com": "USPS",
    "fedex.com": "FedEx",
    "ups.com": "UPS",
    "dhl.com": "DHL",
    "irs.gov": "IRS",
    "yahoo.com": "Yahoo",
    "outlook.com": "Outlook",
    "ebay.com": "eBay",
    "spotify.com": "Spotify",
    "zoom.us": "Zoom",
    "slack.com": "Slack",
    "github.com": "GitHub",
}

# ─── Suspicious TLDs ─────────────────────────────────────────────────────────
#
# TLDs frequently associated with phishing campaigns due to low cost
# and minimal registration requirements.

SUSPICIOUS_TLDS = {
    ".xyz": "Very low-cost TLD, frequently used in phishing",
    ".top": "Commonly used in bulk-registered phishing domains",
    ".buzz": "High abuse rate in phishing campaigns",
    ".club": "Low-cost TLD with elevated abuse metrics",
    ".info": "Historically higher phishing usage than average",
    ".click": "Action-oriented TLD popular in phishing",
    ".link": "Commonly used in deceptive link domains",
    ".work": "Often used in employment-related phishing",
    ".date": "High abuse rate in romance/dating scams",
    ".racing": "Frequently used in redirect-based phishing",
    ".win": "Prize/lottery scam association",
    ".bid": "Auction/financial scam association",
    ".stream": "High abuse rate domain",
    ".gq": "Free TLD — very high abuse rate",
    ".ml": "Free TLD — very high abuse rate",
    ".cf": "Free TLD — very high abuse rate",
    ".tk": "Free TLD — historically highest abuse rate",
    ".ga": "Free TLD — very high abuse rate",
}


def analyze_domain(sender_domain):
    """
    Perform offline heuristic analysis of a sender's domain.

    Parameters
    ----------
    sender_domain : str
        The domain portion of the sender's email address
        (e.g., "example.com").

    Returns
    -------
    dict
        {
            "domain": str,
            "findings": [
                {"type": str, "severity": str, "title": str,
                 "description": str, "evidence": str},
                ...
            ],
            "risk_indicators": int,
            "summary": str,
        }
    """
    try:
        if not sender_domain:
            return _empty_result("")

        domain = sender_domain.lower().strip()
        findings = []

        # 1. Domain age/quality indicators
        findings.extend(_analyze_domain_patterns(domain))

        # 2. Suspicious TLD check
        findings.extend(_check_suspicious_tld(domain))

        # 3. Brand lookalike detection
        findings.extend(_detect_lookalikes(domain))

        # 4. Domain entropy/randomness
        findings.extend(_check_domain_entropy(domain))

        risk_indicators = len(findings)
        summary = _generate_summary(domain, findings)

        return {
            "domain": domain,
            "findings": findings,
            "risk_indicators": risk_indicators,
            "summary": summary,
        }

    except Exception:
        return _empty_result(sender_domain)


def _analyze_domain_patterns(domain):
    """
    Analyze the domain string for patterns associated with disposable
    or recently registered phishing domains.
    """
    findings = []
    # Extract base domain (without TLD)
    parts = domain.rsplit(".", 1)
    base = parts[0] if parts else domain

    # Check for excessive hyphens (e.g., "secure-login-paypal-verify.com")
    hyphen_count = base.count("-")
    if hyphen_count >= 3:
        findings.append({
            "type": "domain_pattern",
            "severity": "medium",
            "title": "Excessive Hyphens",
            "description": (
                f"The domain contains {hyphen_count} hyphens. Legitimate domains "
                f"rarely use more than one hyphen. Multiple hyphens are common in "
                f"phishing domains that try to include brand names."
            ),
            "evidence": domain,
        })

    # Check for digit-heavy domains (e.g., "secure123login456.com")
    digits = sum(1 for c in base if c.isdigit())
    if len(base) > 5 and digits / len(base) > 0.3:
        findings.append({
            "type": "domain_pattern",
            "severity": "medium",
            "title": "Digit-Heavy Domain",
            "description": (
                f"The domain is {int(digits/len(base)*100)}% digits. "
                f"Legitimate domains rarely contain many numbers. "
                f"Phishing domains often use numbers to create variations."
            ),
            "evidence": domain,
        })

    # Check for very long domain names
    if len(base) > 25:
        findings.append({
            "type": "domain_pattern",
            "severity": "low",
            "title": "Unusually Long Domain",
            "description": (
                f"The domain base is {len(base)} characters long. "
                f"Excessively long domains are sometimes used to hide "
                f"the true nature of the URL from casual inspection."
            ),
            "evidence": domain,
        })

    # Check for embedded brand names with extra chars
    brands_in_domain = []
    for brand_domain, brand_name in KNOWN_BRANDS.items():
        brand_base = brand_domain.split(".")[0]
        if brand_base in base and base != brand_base:
            brands_in_domain.append(brand_name)

    if brands_in_domain:
        findings.append({
            "type": "brand_embedding",
            "severity": "high",
            "title": "Brand Name Embedded",
            "description": (
                f"The domain contains the brand name(s) "
                f"{', '.join(brands_in_domain)} but is not the official domain. "
                f"This is a common technique to impersonate legitimate services."
            ),
            "evidence": domain,
        })

    return findings


def _check_suspicious_tld(domain):
    """Check if the domain uses a known suspicious TLD."""
    findings = []

    for tld, reason in SUSPICIOUS_TLDS.items():
        if domain.endswith(tld):
            findings.append({
                "type": "suspicious_tld",
                "severity": "medium",
                "title": f"Suspicious TLD: {tld}",
                "description": f"{reason}. While not all {tld} domains are "
                               f"malicious, this TLD has a statistically higher "
                               f"association with phishing campaigns.",
                "evidence": domain,
            })
            break

    return findings


def _detect_lookalikes(domain):
    """
    Detect domain lookalikes using Levenshtein distance.

    Lookalike domains (e.g., "paypa1.com", "gogle.com") are a common
    phishing technique called typosquatting.
    """
    findings = []
    base = domain.rsplit(".", 1)[0] if "." in domain else domain

    for brand_domain, brand_name in KNOWN_BRANDS.items():
        brand_base = brand_domain.split(".")[0]

        # Skip exact matches (legitimate)
        if domain == brand_domain:
            continue

        # Only compare similar-length domains
        if abs(len(base) - len(brand_base)) > 3:
            continue

        distance = _levenshtein_distance(base, brand_base)

        # Flag if edit distance is 1-2 (suspicious lookalike)
        if 1 <= distance <= 2:
            findings.append({
                "type": "lookalike",
                "severity": "high",
                "title": f"Possible Lookalike: {brand_name}",
                "description": (
                    f"The domain '{domain}' is very similar to '{brand_domain}' "
                    f"(edit distance: {distance}). This could be a typosquatting "
                    f"attempt to impersonate {brand_name}."
                ),
                "evidence": f"{domain} ≈ {brand_domain} (distance: {distance})",
            })

    return findings


def _check_domain_entropy(domain):
    """
    Check for randomly generated domain names.

    Random character strings suggest automatically generated domains,
    which are commonly used in phishing infrastructure.
    """
    findings = []
    base = domain.rsplit(".", 1)[0] if "." in domain else domain
    # Remove hyphens for entropy check
    alpha_base = base.replace("-", "")

    if len(alpha_base) < 6:
        return findings

    # Check consonant-to-vowel ratio
    vowels = sum(1 for c in alpha_base.lower() if c in "aeiou")
    consonants = sum(1 for c in alpha_base.lower() if c.isalpha() and c not in "aeiou")

    if consonants > 0 and vowels > 0:
        ratio = consonants / vowels
        # Natural English has ~1.5-2.5 ratio; random strings tend to be higher
        if ratio > 4.0 and len(alpha_base) > 8:
            findings.append({
                "type": "entropy",
                "severity": "low",
                "title": "Unusual Character Distribution",
                "description": (
                    "The domain has an unusual consonant-to-vowel ratio, "
                    "suggesting it may be randomly generated. Auto-generated "
                    "domains are commonly used in disposable phishing infrastructure."
                ),
                "evidence": f"Consonant:vowel ratio = {ratio:.1f}:1",
            })

    return findings


def _levenshtein_distance(s1, s2):
    """
    Compute the Levenshtein edit distance between two strings.

    This is the minimum number of single-character edits (insertions,
    deletions, or substitutions) needed to transform s1 into s2.
    """
    if len(s1) < len(s2):
        return _levenshtein_distance(s2, s1)

    if len(s2) == 0:
        return len(s1)

    previous_row = range(len(s2) + 1)

    for i, c1 in enumerate(s1):
        current_row = [i + 1]
        for j, c2 in enumerate(s2):
            cost = 0 if c1 == c2 else 1
            current_row.append(min(
                current_row[j] + 1,        # insertion
                previous_row[j + 1] + 1,   # deletion
                previous_row[j] + cost,     # substitution
            ))
        previous_row = current_row

    return previous_row[-1]


def _generate_summary(domain, findings):
    """Generate a human-readable summary of domain analysis."""
    if not findings:
        return (
            f"The domain '{domain}' does not exhibit any suspicious "
            f"infrastructure patterns. No heuristic red flags detected."
        )

    high = sum(1 for f in findings if f["severity"] == "high")
    medium = sum(1 for f in findings if f["severity"] == "medium")

    if high >= 2:
        return (
            f"⚠️ The domain '{domain}' exhibits multiple high-severity "
            f"infrastructure indicators. These heuristics strongly suggest "
            f"a domain set up for phishing purposes."
        )

    if high >= 1 or medium >= 2:
        return (
            f"The domain '{domain}' shows suspicious infrastructure patterns. "
            f"These are advisory indicators — verify the sender independently."
        )

    return (
        f"The domain '{domain}' has minor infrastructure observations. "
        f"These are weak signals and should be considered alongside other evidence."
    )


def _empty_result(domain):
    """Return an empty result structure."""
    return {
        "domain": domain,
        "findings": [],
        "risk_indicators": 0,
        "summary": "Domain analysis unavailable.",
    }
"""

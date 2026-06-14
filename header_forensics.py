import re
import config
# from phishing_engine import Finding, EmailData

def extract_domain(email_addr: str) -> str:
    """Extract domain from an email address."""
    if not email_addr:
        return ""
    match = re.search(r"@([\w.-]+)", email_addr)
    return match.group(1).lower() if match else ""

def analyze_authentication_results(headers: dict) -> list:
    """
    Analyze Authentication-Results and Received-SPF headers for failures.
    """
    from phishing_engine import Finding
    findings = []
    auth_results = headers.get("Authentication-Results", "").lower()
    received_spf = headers.get("Received-SPF", "").lower()
    
    # SPF Analysis
    if "spf=fail" in auth_results or "spf=softfail" in auth_results or "fail" in received_spf:
        score = 25.0 if "fail" in auth_results else 15.0
        findings.append(Finding(
            analyzer="header_forensics",
            indicator="spf_fail",
            score=score,
            evidence=f"SPF Validation Failed",
            explanation=(
                "The email failed the Sender Policy Framework (SPF) check. "
                "This means the sending server is not authorized to send emails "
                "on behalf of this domain. This is a strong indicator of spoofing."
            )
        ))

    # DKIM Analysis
    if "dkim=fail" in auth_results:
         findings.append(Finding(
            analyzer="header_forensics",
            indicator="dkim_fail",
            score=25.0,
            evidence="DKIM Validation Failed",
            explanation=(
                "The email failed DomainKeys Identified Mail (DKIM) validation. "
                "This means the email content may have been tampered with in transit, "
                "or the sender is not who they claim to be."
            )
        ))

    # DMARC Analysis
    if "dmarc=fail" in auth_results:
         findings.append(Finding(
            analyzer="header_forensics",
            indicator="dmarc_fail",
            score=30.0,
            evidence="DMARC Validation Failed",
            explanation=(
                "The email failed DMARC authentication. This protocol relies on SPF "
                "and DKIM. A failure here strongly suggests the email is fraudulent "
                "and should not be trusted."
            )
        ))
        
    return findings

def analyze_routing(email: object, headers: dict) -> list:
    """
    Analyze routing information (Return-Path vs From).
    """
    from phishing_engine import Finding
    findings = []
    return_path = headers.get("Return-Path", "")
    from_header = email.sender_raw
    
    if not return_path or not from_header:
        # Sometimes Return-Path is missing in internal/system emails
        return findings

    # Clean up formatting <angle brackets>
    return_path_clean = return_path.strip("<> ")
    
    rp_domain = extract_domain(return_path_clean)
    from_domain = extract_domain(from_header)
    
    # Allow subdomains relationships e.g. bounces@notifications.google.com vs google.com
    # But flag unrelated domains e.g. attacker-server.com vs google.com
    
    if rp_domain and from_domain and rp_domain != from_domain:
        # Check if one is subdomain of another
        if not (rp_domain.endswith("." + from_domain) or from_domain.endswith("." + rp_domain)):
             # Check for common ESP patterns (SendGrid, MailChimp, Amazon SES etc usually end with .com and have random prefixes)
             # But for pure phishing detection, a mismatch IS suspicious unless allowed by SPF (which we check separately).
             # We will give a moderate score for mismatch.
             
             findings.append(Finding(
                analyzer="header_forensics",
                indicator="domain_mismatch",
                score=10.0,
                evidence=f"Return-Path: {rp_domain} != From: {from_domain}",
                explanation=(
                    f"The email was sent from '{rp_domain}' but claims to be from '{from_domain}'. "
                    "This mismatch is common in spoofing attempts, although some bulk email services also do this."
                )
             ))

    return findings

def analyze_headers(email: object) -> list:
    """
    Master function for header analysis.
    Wait! EmailData doesn't have a 'headers' field yet. 
    I need to update EmailData to include headers dict OR pass headers separately.
    The plan said: "Update EmailData to include a headers: dict field."
    So I should access email.headers.
    """
    # Assuming email.headers exists as per plan
    if not hasattr(email, 'headers'):
        return []
        
    findings = []
    findings.extend(analyze_authentication_results(email.headers))
    findings.extend(analyze_routing(email, email.headers))
    
    return findings

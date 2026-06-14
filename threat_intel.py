
import config

def check_url_reputation(url: str) -> dict:
    """
    Simulate checking a URL against external Threat Intelligence sources 
    (VirusTotal, Google Safe Browsing).
    
    In a production env, this would make HTTP requests to APIs using keys from config.
    For this demo, we check against a curated list of known bad indicators.
    
    Returns:
        {
            "score": int (0-100),
            "classification": str ('malicious', 'suspicious', 'clean'),
            "source": str
        }
    """
    url_lower = url.lower()
    
    # 1. Known Malicious Domains (Mock Threat Feed)
    malicious_domains = [
        "login-secure-update.com",
        "verify-account-now.net",
        "free-crypto-giveaway.org",
        "apple-id-reset.tk",
        "paypal-security-alert.ml"
    ]
    
    for bad_domain in malicious_domains:
        if bad_domain in url_lower:
            return {
                "score": 100,
                "classification": "malicious",
                "source": "Mock Threat Feed (Blacklist)"
            }
            
    # 2. Suspicious TLDs
    suspicious_tlds = [".tk", ".ml", ".ga", ".cf", ".gq", ".top", ".xyz"]
    for tld in suspicious_tlds:
        if url_lower.endswith(tld) or (tld + "/") in url_lower:
            return {
                "score": 75,
                "classification": "suspicious",
                "source": "Heuristic (High-Risk TLD)"
            }

    # 3. Keyword in Domain (e.g. "secure-login")
    if "login" in url_lower and "secure" in url_lower and "https" not in url_lower:
         return {
                "score": 60,
                "classification": "suspicious",
                "source": "Heuristic (Deceptive Pattern)"
            }
            
    return {
        "score": 0,
        "classification": "clean",
        "source": "Clean"
    }

def batch_check_urls(urls: list) -> list:
    """Check multiple URLs."""
    results = []
    for url in urls:
        res = check_url_reputation(url)
        if res['score'] > 0:
            results.append({
                "url": url,
                "analysis": res
            })
    return results

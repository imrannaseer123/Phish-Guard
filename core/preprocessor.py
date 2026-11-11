"""
Email Preprocessing Module
─────────────────────────
Normalizes email content, extracts URLs, detects shortened links,
and parses sender information for analysis.
"""

import re
from urllib.parse import urlparse
from bs4 import BeautifulSoup
import tldextract

import config


def strip_html(html_content: str) -> str:
    """Remove HTML tags and return plain text."""
    if not html_content:
        return ""
    soup = BeautifulSoup(html_content, "html.parser")
    # Remove script and style elements
    for tag in soup(["script", "style"]):
        tag.decompose()
    text = soup.get_text(separator=" ")
    # Collapse whitespace
    text = re.sub(r"\s+", " ", text).strip()
    return text


def normalize_text(text: str) -> str:
    """Lowercase and normalize whitespace."""
    if not text:
        return ""
    return re.sub(r"\s+", " ", text.strip().lower())


def extract_urls(text: str) -> list[str]:
    """Extract all URLs from text."""
    if not text:
        return []
    url_pattern = re.compile(
        r"https?://[^\s<>\"'\)]+|www\.[^\s<>\"'\)]+"
    )
    urls = url_pattern.findall(text)
    return [u.rstrip(".,;:!?)") for u in urls]


def extract_urls_from_html(html_content: str) -> list[dict]:
    """
    Extract URLs from HTML anchor tags, keeping both href and display text.
    Returns list of {'href': ..., 'display_text': ...}.
    """
    if not html_content:
        return []
    soup = BeautifulSoup(html_content, "html.parser")
    results = []
    for a_tag in soup.find_all("a", href=True):
        href = a_tag["href"].strip()
        display = a_tag.get_text(strip=True)
        if href.startswith(("http://", "https://", "www.")):
            results.append({"href": href, "display_text": display})
    return results


def is_shortened_url(url: str) -> bool:
    """Check if a URL uses a known shortening service."""
    try:
        parsed = urlparse(url if url.startswith("http") else f"http://{url}")
        domain = parsed.netloc.lower().lstrip("www.")
        return domain in config.SHORTENED_URL_DOMAINS
    except Exception:
        return False


def is_ip_based_url(url: str) -> bool:
    """Check if a URL uses an IP address instead of a domain."""
    try:
        parsed = urlparse(url if url.startswith("http") else f"http://{url}")
        host = parsed.hostname or ""
        ip_pattern = re.compile(r"^\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}$")
        return bool(ip_pattern.match(host))
    except Exception:
        return False


def count_subdomains(url: str) -> int:
    """Count the number of subdomains in a URL."""
    try:
        extracted = tldextract.extract(url)
        subdomain = extracted.subdomain
        if not subdomain:
            return 0
        return len(subdomain.split("."))
    except Exception:
        return 0


def parse_sender(from_header: str) -> dict:
    """
    Parse the From header into display_name and email/domain.
    Examples:
        'John Doe <john@example.com>' → {'display_name': 'John Doe', 'email': 'john@example.com', 'domain': 'example.com'}
        'john@example.com' → {'display_name': '', 'email': 'john@example.com', 'domain': 'example.com'}
    """
    result = {"display_name": "", "email": "", "domain": ""}
    if not from_header:
        return result

    # Match "Name <email>" pattern
    match = re.match(r"^(.*?)\s*<([^>]+)>", from_header)
    if match:
        result["display_name"] = match.group(1).strip().strip('"').strip("'")
        result["email"] = match.group(2).strip().lower()
    else:
        # Just an email address
        email_match = re.search(r"[\w\.\+\-]+@[\w\.\-]+\.\w+", from_header)
        if email_match:
            result["email"] = email_match.group(0).lower()

    if result["email"] and "@" in result["email"]:
        result["domain"] = result["email"].split("@")[1]

    return result


def has_excessive_caps(text: str, threshold: float = 0.5) -> bool:
    """Check if more than `threshold` fraction of alphabetic chars are uppercase."""
    if not text:
        return False
    alpha_chars = [c for c in text if c.isalpha()]
    if len(alpha_chars) < 10:
        return False
    upper_count = sum(1 for c in alpha_chars if c.isupper())
    return (upper_count / len(alpha_chars)) > threshold


def has_excessive_punctuation(text: str, threshold: int = 5) -> bool:
    """Check for excessive exclamation marks or question marks."""
    if not text:
        return False
    exclamation_count = text.count("!")
    question_count = text.count("?")
    return exclamation_count >= threshold or question_count >= threshold

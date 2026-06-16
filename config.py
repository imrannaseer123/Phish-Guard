"""
Central configuration for the Phishing Email Risk Analyzer.
All thresholds, keyword lists, scoring weights, and paths are defined here.
"""

import os

# ─── Paths ────────────────────────────────────────────────────────────────────
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATABASE_PATH = os.path.join(BASE_DIR, "phishing_logs.db")
CREDENTIALS_FILE = os.path.join(BASE_DIR, "credentials.json")
TOKEN_FILE = os.path.join(BASE_DIR, "token.json")

# ─── Flask ────────────────────────────────────────────────────────────────────
SECRET_KEY = os.environ.get("FLASK_SECRET_KEY", "phishing-analyzer-dev-key-change-in-prod")
DEBUG = True
PORT = 5000

# ─── Gmail OAuth ──────────────────────────────────────────────────────────────
GMAIL_SCOPES = ["https://www.googleapis.com/auth/gmail.readonly"]
MAX_INBOX_RESULTS = 20

# ─── Risk Thresholds ─────────────────────────────────────────────────────────
RISK_LOW_MAX = 33
RISK_MEDIUM_MAX = 66
# Above RISK_MEDIUM_MAX → High

# ─── Scoring Weights (max contribution per analyzer) ─────────────────────────
SCORE_WEIGHTS = {
    "keyword":   25,
    "url":       25,
    "sender":    20,
    "urgency":   15,
    "structure": 15,
}

# ─── Suspicious Keywords ─────────────────────────────────────────────────────
PHISHING_KEYWORDS = [
    # Credential harvesting
    "verify your account", "confirm your identity", "update your information",
    "validate your account", "re-verify", "reconfirm your details",
    "log in immediately", "sign in to your account",
    # Urgency / threats
    "account suspended", "account will be closed", "unauthorized access",
    "unusual activity", "suspicious activity", "security alert",
    "your account has been compromised", "immediate action required",
    "failure to respond will result", "within 24 hours", "within 48 hours",
    # Financial lures
    "you have won", "claim your prize", "lottery winner",
    "bank transfer", "wire transfer", "tax refund",
    "inheritance fund", "unclaimed funds", "payment pending",
    # Action demands
    "click here", "click the link below", "click immediately",
    "download the attachment", "open the attached",
    "reset your password", "change your password now",
    # Impersonation
    "dear customer", "dear valued customer", "dear user",
    "dear account holder", "dear sir/madam",
    # Threats
    "legal action", "law enforcement", "criminal charges",
    "account termination", "service interruption",
]

URGENCY_PHRASES = [
    "act now", "act immediately", "urgent", "immediately",
    "as soon as possible", "asap", "time sensitive", "expires today",
    "final notice", "final warning", "last chance", "limited time",
    "deadline", "don't delay", "do not ignore", "respond immediately",
    "time is running out", "hurry", "expiring soon",
]

# ─── Shortened URL Domains ───────────────────────────────────────────────────
SHORTENED_URL_DOMAINS = [
    "bit.ly", "tinyurl.com", "t.co", "goo.gl", "ow.ly",
    "is.gd", "buff.ly", "adf.ly", "tiny.cc", "lnkd.in",
    "rb.gy", "cutt.ly", "shorturl.at", "rebrand.ly",
]

# ─── Free Email Providers ────────────────────────────────────────────────────
FREE_EMAIL_PROVIDERS = [
    "gmail.com", "yahoo.com", "hotmail.com", "outlook.com",
    "aol.com", "mail.com", "protonmail.com", "zoho.com",
    "yandex.com", "icloud.com", "gmx.com", "live.com",
]

# ─── Credential Request Indicators ───────────────────────────────────────────
CREDENTIAL_KEYWORDS = [
    "password", "username", "social security", "ssn",
    "credit card", "card number", "cvv", "pin",
    "bank account", "routing number", "login credentials",
    "date of birth", "mother's maiden name",
]

# ─── Phishing Intent Categories ──────────────────────────────────────────────
INTENT_CATEGORIES = [
    "Credential Harvesting",
    "Financial Fraud",
    "Malware Delivery",
    "Identity Theft",
    "Legitimate",
]

# ─── Privacy & AI Configuration ──────────────────────────────────────────────
PII_REDACTION_ENABLED = True
ENABLE_CHATBOT = True
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY", "use your gemini api key from google console - here") # Get from env or set here
CHATBOT_MODEL = "gemini-flash-latest"

# ─── External Threat Intelligence ────────────────────────────────────────────
VIRUSTOTAL_API_KEY = os.environ.get("VIRUSTOTAL_API_KEY", "")
GOOGLE_SAFE_BROWSING_KEY = os.environ.get("GOOGLE_SAFE_BROWSING_KEY", "")

# ─── Header Route Visualization ──────────────────────────────────────────────
HEADER_GRAPH_ENABLED = True

# ─── ASCEND Framework ─────────────────────────────────────────────────────
# Master toggle for the entire ASCEND add-on layer.
# When False, all ASCEND features are silently disabled and the app
# behaves exactly as before.
ASCEND_ENABLED = True

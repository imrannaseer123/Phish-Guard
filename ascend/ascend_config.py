"""
ascend Configuration
───────────────────────
Per-feature enable/disable flags, thresholds, and keyword
dictionaries. All features default to enabled.

⚠️  This file is SEPARATE from core config.py —
    it controls only ascend add-on behaviour.
"""

# ─── Feature Flags ────────────────────────────────────────────────────────────
# Set any to False to silently disable that feature.

COUNTERFACTUAL_ENABLED = True
THREAT_ONTOLOGY_ENABLED = True
RISK_FORECAST_ENABLED = True
PSYCH_ANALYZER_ENABLED = True
RULE_FEEDBACK_ENABLED = True
INCIDENT_REPORTER_ENABLED = True
WHATIF_SANDBOX_ENABLED = True

# ─── Incident Reporter ───────────────────────────────────────────────────────
INCIDENT_THRESHOLD = 80  # Minimum risk score to trigger incident report

# ─── Risk Forecast ────────────────────────────────────────────────────────────
FORECAST_WINDOW = 20     # Number of recent analyses for SMA calculation
FORECAST_HIGH_FREQ_THRESHOLD = 0.4  # >40% high-risk → High vulnerability

# ─── Psychological Manipulation Keywords ──────────────────────────────────────
# Each keyword has an intensity: 1 = low, 2 = medium, 3 = high
# Categories: Fear, Urgency, Reward, Authority

PSYCH_KEYWORDS = {
    "fear": {
        # High intensity — direct threats
        "your account will be closed": 3,
        "account suspended": 3,
        "unauthorized access detected": 3,
        "your account has been compromised": 3,
        "criminal charges": 3,
        "legal action": 3,
        "law enforcement": 3,
        "permanent ban": 3,
        # Medium intensity — implied consequences
        "suspicious activity": 2,
        "unusual activity": 2,
        "security breach": 2,
        "account termination": 2,
        "service interruption": 2,
        "failure to respond": 2,
        "data loss": 2,
        # Low intensity — vague warnings
        "security alert": 1,
        "important notice": 1,
        "warning": 1,
        "risk": 1,
    },
    "urgency": {
        # High intensity — hard deadlines
        "within 24 hours": 3,
        "within 48 hours": 3,
        "expires today": 3,
        "act now": 3,
        "immediate action required": 3,
        "act immediately": 3,
        # Medium intensity — soft deadlines
        "as soon as possible": 2,
        "time sensitive": 2,
        "limited time": 2,
        "don't delay": 2,
        "hurry": 2,
        "time is running out": 2,
        # Low intensity — general urgency
        "urgent": 1,
        "asap": 1,
        "final notice": 1,
        "last chance": 1,
        "respond immediately": 1,
    },
    "reward": {
        # High intensity — large promises
        "you have won": 3,
        "claim your prize": 3,
        "lottery winner": 3,
        "inheritance fund": 3,
        "unclaimed funds": 3,
        "million dollars": 3,
        # Medium intensity — financial lures
        "tax refund": 2,
        "payment pending": 2,
        "exclusive offer": 2,
        "special promotion": 2,
        "free gift": 2,
        "bonus": 2,
        # Low intensity — minor incentives
        "reward": 1,
        "congratulations": 1,
        "selected": 1,
        "eligible": 1,
    },
    "authority": {
        # High intensity — direct impersonation
        "official notice": 3,
        "government agency": 3,
        "internal revenue": 3,
        "federal bureau": 3,
        "compliance department": 3,
        # Medium intensity — corporate impersonation
        "security team": 2,
        "account verification team": 2,
        "customer support team": 2,
        "system administrator": 2,
        "it department": 2,
        # Low intensity — generic authority
        "dear customer": 1,
        "dear valued customer": 1,
        "dear account holder": 1,
        "management": 1,
        "administrator": 1,
    },
}

# ─── Threat Ontology Knowledge Graph ─────────────────────────────────────────
# Maps evidence indicators → intent → impact
# Structure: { evidence_indicator: [{ intent, impact, description }] }

ONTOLOGY_MAP = {
    # URL-based evidence
    "shortened_url": [
        {
            "intent": "Obfuscation",
            "impact": "Credential Theft",
            "description": "Shortened URLs hide the true destination, enabling redirect to phishing pages.",
        }
    ],
    "ip_based_url": [
        {
            "intent": "Infrastructure Concealment",
            "impact": "Malware Distribution",
            "description": "IP-based URLs bypass domain reputation checks, often hosting ephemeral attack infrastructure.",
        }
    ],
    "excessive_subdomains": [
        {
            "intent": "Visual Deception",
            "impact": "Credential Theft",
            "description": "Deep subdomain structures mimic legitimate domains to confuse victims.",
        }
    ],
    "anchor_mismatch": [
        {
            "intent": "Link Manipulation",
            "impact": "Credential Theft",
            "description": "Display text differs from actual URL — a classic phishing technique to build false trust.",
        }
    ],
    # Sender-based evidence
    "brand_impersonation": [
        {
            "intent": "Social Engineering",
            "impact": "Identity Theft",
            "description": "Sender impersonates a trusted brand to exploit victim's trust relationship.",
        }
    ],
    "free_email_corporate": [
        {
            "intent": "Credential Harvesting",
            "impact": "Account Takeover",
            "description": "Using free email to impersonate corporate entities indicates low-effort phishing campaigns.",
        }
    ],
    "display_name_mismatch": [
        {
            "intent": "Impersonation",
            "impact": "Identity Theft",
            "description": "Display name doesn't match the actual sender domain, suggesting spoofing.",
        }
    ],
    "reply_to_mismatch": [
        {
            "intent": "Response Hijacking",
            "impact": "Information Exfiltration",
            "description": "Reply-to address differs from sender, routing victim responses to attacker-controlled inbox.",
        }
    ],
    # Content-based evidence
    "phishing_keyword": [
        {
            "intent": "Social Engineering",
            "impact": "Credential Theft",
            "description": "Common phishing phrases designed to trigger immediate action without verification.",
        }
    ],
    "credential_request": [
        {
            "intent": "Credential Harvesting",
            "impact": "Account Takeover",
            "description": "Direct solicitation of passwords, PINs, or banking details for unauthorized access.",
        }
    ],
    "urgency_phrase": [
        {
            "intent": "Psychological Pressure",
            "impact": "Rushed Decision-Making",
            "description": "Time-pressure language bypasses rational decision-making processes.",
        }
    ],
    "excessive_caps": [
        {
            "intent": "Attention Manipulation",
            "impact": "Emotional Response Trigger",
            "description": "ALL CAPS text creates visual urgency and emotional arousal.",
        }
    ],
    "excessive_punctuation": [
        {
            "intent": "Emotional Manipulation",
            "impact": "Panic Inducement",
            "description": "Excessive exclamation marks amplify perceived urgency and importance.",
        }
    ],
    # Structure-based evidence
    "generic_greeting": [
        {
            "intent": "Mass Campaign",
            "impact": "Wide-Scale Phishing",
            "description": "Generic greetings indicate untargeted mass phishing campaign.",
        }
    ],
    "no_greeting": [
        {
            "intent": "Automated Attack",
            "impact": "Indiscriminate Targeting",
            "description": "Absence of greeting suggests automated email generation.",
        }
    ],
    "grammar_issues": [
        {
            "intent": "Foreign-Origin Attack",
            "impact": "Reduced Legitimacy",
            "description": "Grammar issues may indicate non-native authorship from foreign threat actors.",
        }
    ],
    # Image/QR-based evidence
    "qr_code_detected": [
        {
            "intent": "Visual Redirect",
            "impact": "Credential Theft",
            "description": "QR codes embedded in emails bypass URL filters and redirect to phishing pages.",
        }
    ],
    "ocr_suspicious_text": [
        {
            "intent": "Filter Evasion",
            "impact": "Hidden Phishing Content",
            "description": "Text embedded in images evades text-based email filters.",
        }
    ],
}

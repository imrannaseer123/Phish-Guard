"""
Security Training Simulation Module (Feature 10)
─────────────────────────────────────────────────
Provides offline simulated phishing examples for security awareness
training. Users can practice identifying phishing emails in a safe,
controlled environment.

Features:
    - 8 realistic phishing scenarios covering different attack types
    - Each scenario includes subject, sender, body, and expected analysis
    - Users can guess risk level before seeing actual analysis
    - Score comparison and educational feedback
    - No real emails sent — entirely offline/simulated

Educational Goals:
    - Help users recognize common phishing tactics
    - Build intuition for evaluating email authenticity
    - Provide feedback loop for learning improvement

Design Constraints:
    - Offline only — no real email sending or receiving
    - All scenarios are hardcoded (no database dependency)
    - Education-only feature — no automated actions
    - Fail-safe: returns empty list on error
"""

from dataclasses import dataclass


# ─── Training Scenarios ──────────────────────────────────────────────────────

TRAINING_SCENARIOS = [
    {
        "id": "scenario_1",
        "difficulty": "Easy",
        "category": "Credential Harvesting",
        "title": "Account Verification Scam",
        "subject": "URGENT: Your account access will be revoked in 24 hours",
        "sender": "security-alert@acc0unt-verify.xyz",
        "body_text": (
            "Dear Valued Customer,\n\n"
            "We have detected unusual activity on your account. Your access "
            "will be permanently revoked within 24 hours unless you verify "
            "your identity immediately.\n\n"
            "Click here to verify your account: http://192.168.1.100/verify\n\n"
            "You must provide your username, password, and security questions "
            "to complete verification.\n\n"
            "Failure to respond will result in permanent account termination.\n\n"
            "Regards,\n"
            "Account Security Team"
        ),
        "expected_risk": "High",
        "expected_score_range": [70, 100],
        "red_flags": [
            "Urgency tactics: '24 hours' deadline",
            "Generic greeting: 'Dear Valued Customer'",
            "IP-based URL instead of domain name",
            "Requests password and security questions",
            "Suspicious sender domain (.xyz TLD)",
            "Threatening language about account termination",
        ],
        "learning_points": [
            "Legitimate services never ask for passwords via email",
            "IP addresses in URLs are a major red flag",
            "Artificial urgency is a classic manipulation technique",
            "Check the sender's actual email domain, not display name",
        ],
    },
    {
        "id": "scenario_2",
        "difficulty": "Easy",
        "category": "Financial Fraud",
        "title": "Lottery Winner Scam",
        "subject": "Congratulations! You've won $1,500,000 in the International Lottery",
        "sender": "lottery-winner@free-prize-claim.top",
        "body_text": (
            "Dear Lucky Winner,\n\n"
            "CONGRATULATIONS!!! Your email was randomly selected in our "
            "annual international lottery draw! You have won the grand prize "
            "of $1,500,000 USD!!!\n\n"
            "To claim your prize, please provide:\n"
            "- Full Name\n"
            "- Bank Account Number\n"
            "- Routing Number\n"
            "- Date of Birth\n\n"
            "Processing fee of $250 must be paid via Western Union to:\n"
            "Agent: Mr. James Williams\n"
            "Location: Lagos, Nigeria\n\n"
            "ACT NOW - This offer expires today!!!\n\n"
            "Sincerely,\n"
            "International Lottery Commission"
        ),
        "expected_risk": "High",
        "expected_score_range": [80, 100],
        "red_flags": [
            "Classic lottery scam pattern",
            "Excessive punctuation (!!!)",
            "Requests bank account details",
            "Advance fee fraud (Western Union payment)",
            "Suspicious TLD (.top)",
            "Too good to be true offer",
        ],
        "learning_points": [
            "You cannot win a lottery you didn't enter",
            "Legitimate prizes never require advance payment",
            "Requests for bank details via email are always fraudulent",
            "Excessive punctuation indicates unprofessional/scam emails",
        ],
    },
    {
        "id": "scenario_3",
        "difficulty": "Medium",
        "category": "Malware Delivery",
        "title": "Fake Invoice Attachment",
        "subject": "Invoice #INV-2024-0847 - Payment Due",
        "sender": "accounting@secure-invoices.club",
        "body_text": (
            "Hi,\n\n"
            "Please find attached the invoice for your recent purchase. "
            "Payment is due within 5 business days.\n\n"
            "Invoice Amount: $3,247.89\n"
            "Due Date: February 15, 2024\n\n"
            "Please download the attached document and enable macros to "
            "view the invoice details.\n\n"
            "If you have questions about this invoice, click here: "
            "http://bit.ly/3xK9mPq\n\n"
            "Thank you for your business.\n\n"
            "Best regards,\n"
            "Accounting Department"
        ),
        "expected_risk": "High",
        "expected_score_range": [60, 90],
        "red_flags": [
            "Instruction to 'enable macros' — malware delivery technique",
            "Shortened URL (bit.ly)",
            "Suspicious sender domain (.club TLD)",
            "Unexpected invoice from unknown sender",
            "Vague company identity",
        ],
        "learning_points": [
            "Never enable macros in unexpected documents",
            "Shortened URLs hide the true destination",
            "Verify invoices through your company's accounting system",
            "Legitimate invoices come from known business contacts",
        ],
    },
    {
        "id": "scenario_4",
        "difficulty": "Medium",
        "category": "Brand Impersonation",
        "title": "Fake Shipping Notification",
        "subject": "Your package delivery failed - Action Required",
        "sender": "FedEx Shipping <tracking@fedex-delivery-update.com>",
        "body_text": (
            "Dear Customer,\n\n"
            "We attempted to deliver your package but were unable to complete "
            "the delivery due to an incomplete address.\n\n"
            "Tracking Number: FX-2847561930\n"
            "Scheduled Delivery: Today\n\n"
            "To reschedule delivery, please confirm your address and pay the "
            "re-delivery fee of $3.99:\n\n"
            "https://fedex-redelivery-confirm.xyz/track?id=2847561930\n\n"
            "If not resolved within 48 hours, your package will be returned "
            "to sender.\n\n"
            "FedEx Customer Service"
        ),
        "expected_risk": "High",
        "expected_score_range": [55, 85],
        "red_flags": [
            "Brand impersonation (FedEx)",
            "Domain is not official fedex.com",
            "Requests payment for 're-delivery fee'",
            "Urgency: '48 hours' deadline",
            "Suspicious URL with .xyz TLD",
            "Generic greeting despite claiming to know your package",
        ],
        "learning_points": [
            "Always go directly to the official website to track packages",
            "FedEx never charges re-delivery fees via email",
            "Check the actual sender email domain, not the display name",
            "Legitimate companies use their own domain for links",
        ],
    },
    {
        "id": "scenario_5",
        "difficulty": "Hard",
        "category": "Credential Harvesting",
        "title": "Sophisticated IT Department Phishing",
        "subject": "Required: Multi-Factor Authentication Update",
        "sender": "IT Security <it-security@company-sso.net>",
        "body_text": (
            "Dear Team Member,\n\n"
            "As part of our ongoing security improvements, we are upgrading "
            "our multi-factor authentication system. All employees must "
            "re-enroll by end of business Friday.\n\n"
            "What you need to do:\n"
            "1. Visit our SSO portal: https://company-sso.net/mfa-update\n"
            "2. Sign in with your current credentials\n"
            "3. Set up your new MFA device\n\n"
            "This is a mandatory security requirement. Accounts that are not "
            "updated will be temporarily locked for compliance purposes.\n\n"
            "If you need assistance, contact the IT Help Desk.\n\n"
            "Best regards,\n"
            "IT Security Team"
        ),
        "expected_risk": "Medium",
        "expected_score_range": [35, 65],
        "red_flags": [
            "Uses a lookalike domain (company-sso.net, not actual company)",
            "Creates urgency with a deadline",
            "Asks users to 'sign in with current credentials'",
            "Threat of account lock for non-compliance",
            "Professional tone masks social engineering",
        ],
        "learning_points": [
            "Even professional-looking emails can be phishing",
            "Verify IT communications through internal channels",
            "Never click SSO links in emails — type the URL directly",
            "Check if the domain matches your actual company domain",
            "This type of spear-phishing is the hardest to detect",
        ],
    },
    {
        "id": "scenario_6",
        "difficulty": "Hard",
        "category": "Identity Theft",
        "title": "Tax Refund Social Engineering",
        "subject": "IRS Tax Refund Notification - Ref #TX-2024-884721",
        "sender": "refunds@irs-tax-portal.com",
        "body_text": (
            "Dear Taxpayer,\n\n"
            "After reviewing your tax records, we have determined that you "
            "are eligible for a tax refund of $4,812.00 for the fiscal year "
            "2023-2024.\n\n"
            "To process your refund, we need to verify your identity:\n"
            "- Full Legal Name\n"
            "- Social Security Number (SSN)\n"
            "- Date of Birth\n"
            "- Current Mailing Address\n"
            "- Bank Account for Direct Deposit\n\n"
            "Please submit your information within 10 business days to avoid "
            "processing delays.\n\n"
            "Submit here: https://irs-tax-portal.com/refund/verify\n\n"
            "This is an official communication from the Internal Revenue Service.\n\n"
            "Regards,\n"
            "IRS Refund Processing Department"
        ),
        "expected_risk": "High",
        "expected_score_range": [65, 95],
        "red_flags": [
            "IRS impersonation — IRS never initiates contact via email",
            "Requests SSN and bank account information",
            "Domain is not irs.gov (uses .com instead)",
            "Promise of refund to lure victim",
            "Urgency with 10-day deadline",
            "Asks for extensive PII",
        ],
        "learning_points": [
            "The IRS never initiates contact via email or text",
            "Government agencies use .gov domains, not .com",
            "Never provide SSN or bank details via email links",
            "Verify tax matters through irs.gov directly",
            "Report IRS impersonation to phishing@irs.gov",
        ],
    },
    {
        "id": "scenario_7",
        "difficulty": "Easy",
        "category": "Legitimate",
        "title": "Genuine Newsletter",
        "subject": "Your Weekly Tech Digest - February 2024",
        "sender": "newsletter@techdigest.com",
        "body_text": (
            "Hi there,\n\n"
            "Here's your weekly tech roundup:\n\n"
            "📱 Top Stories This Week:\n"
            "1. Apple announces new MacBook Pro with M4 chip\n"
            "2. Google releases major Android update\n"
            "3. Microsoft expands AI features in Office 365\n\n"
            "📊 Developer Corner:\n"
            "- Python 3.13 beta is now available for testing\n"
            "- React 19 brings exciting new hooks\n\n"
            "Read the full digest on our website:\n"
            "https://techdigest.com/weekly/feb-2024\n\n"
            "To unsubscribe, click here:\n"
            "https://techdigest.com/preferences/unsubscribe\n\n"
            "Happy reading!\n"
            "The TechDigest Team"
        ),
        "expected_risk": "Low",
        "expected_score_range": [0, 15],
        "red_flags": [],
        "learning_points": [
            "This email is LEGITIMATE — not all emails are phishing",
            "Consistent sender domain (techdigest.com)",
            "No urgency, threats, or requests for sensitive info",
            "Professional formatting with clear unsubscribe option",
            "It's important to recognize safe emails too!",
        ],
    },
    {
        "id": "scenario_8",
        "difficulty": "Hard",
        "category": "Credential Harvesting",
        "title": "Shared Document Phishing",
        "subject": "Document shared with you: Q4 Financial Report.pdf",
        "sender": "Sarah Chen <sarah.chen@outlook.com>",
        "body_text": (
            "Hi,\n\n"
            "I've shared the Q4 financial report with you. Please review "
            "it before our meeting tomorrow.\n\n"
            "View document: https://docs-cloud-share.click/view?d=q4report\n\n"
            "You'll need to sign in with your work email to access the "
            "document.\n\n"
            "Thanks,\n"
            "Sarah"
        ),
        "expected_risk": "Medium",
        "expected_score_range": [30, 60],
        "red_flags": [
            "Suspicious URL domain (docs-cloud-share.click, not a real service)",
            ".click is a suspicious TLD",
            "Asks to 'sign in with work email' — credential harvesting",
            "Sender uses personal email for business document",
            "Short, pressuring context ('before our meeting tomorrow')",
        ],
        "learning_points": [
            "Verify shared documents through official platforms",
            "Be suspicious of unfamiliar document sharing URLs",
            "Legitimate services like Google Docs use their own domains",
            "Contact the sender through another channel to verify",
            "Short, context-light emails with links deserve scrutiny",
        ],
    },
]


def get_training_scenarios():
    """
    Get all available training scenarios.

    Returns
    -------
    list[dict]
        List of training scenarios with metadata (no analysis).
    """
    try:
        return [
            {
                "id": s["id"],
                "difficulty": s["difficulty"],
                "category": s["category"],
                "title": s["title"],
                "subject": s["subject"],
                "sender": s["sender"],
            }
            for s in TRAINING_SCENARIOS
        ]
    except Exception:
        return []


def get_scenario_detail(scenario_id):
    """
    Get the full detail for a specific training scenario.

    Parameters
    ----------
    scenario_id : str
        The scenario identifier.

    Returns
    -------
    dict or None
        Full scenario data, or None if not found.
    """
    try:
        for s in TRAINING_SCENARIOS:
            if s["id"] == scenario_id:
                return s
        return None
    except Exception:
        return None


def evaluate_user_guess(scenario_id, user_guess):
    """
    Evaluate a user's risk level guess against the expected answer.

    Parameters
    ----------
    scenario_id : str
        The scenario identifier.
    user_guess : str
        The user's guess: "Low", "Medium", or "High".

    Returns
    -------
    dict
        {
            "correct": bool,
            "expected": str,
            "user_guess": str,
            "red_flags": list[str],
            "learning_points": list[str],
            "feedback": str,
        }
    """
    try:
        scenario = get_scenario_detail(scenario_id)
        if not scenario:
            return {"correct": False, "feedback": "Scenario not found."}

        expected = scenario["expected_risk"]
        correct = (user_guess == expected)

        if correct:
            feedback = (
                f"✅ Correct! This email is indeed {expected} risk. "
                f"Well done — you identified the key indicators."
            )
        else:
            feedback = (
                f"❌ Not quite. This email is actually {expected} risk "
                f"(you guessed {user_guess}). Review the red flags below "
                f"to understand why."
            )

        return {
            "correct": correct,
            "expected": expected,
            "user_guess": user_guess,
            "red_flags": scenario["red_flags"],
            "learning_points": scenario["learning_points"],
            "feedback": feedback,
            "scenario_title": scenario["title"],
            "category": scenario["category"],
        }

    except Exception:
        return {"correct": False, "feedback": "Evaluation error."}


def get_training_stats():
    """
    Get training module statistics.

    Returns
    -------
    dict
        Overview of available training content.
    """
    try:
        total = len(TRAINING_SCENARIOS)
        by_difficulty = {}
        by_category = {}

        for s in TRAINING_SCENARIOS:
            diff = s["difficulty"]
            cat = s["category"]
            by_difficulty[diff] = by_difficulty.get(diff, 0) + 1
            by_category[cat] = by_category.get(cat, 0) + 1

        return {
            "total_scenarios": total,
            "by_difficulty": by_difficulty,
            "by_category": by_category,
        }
    except Exception:
        return {"total_scenarios": 0, "by_difficulty": {}, "by_category": {}}

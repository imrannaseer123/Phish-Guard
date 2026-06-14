"""
Test Engine -- Standalone test for the phishing detection pipeline.
Runs sample emails through the engine without requiring Gmail credentials.
"""

import sys
import os

# Ensure project root is in path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Fix Windows console encoding
if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

from phishing_engine import EmailData, analyze_email
from risk_scorer import generate_report


def separator(title: str):
    print(f"\n{'=' * 70}")
    print(f"  {title}")
    print(f"{'=' * 70}")


def print_report(report, email_label: str):
    """Pretty-print a risk report."""
    print(f"\n📧 Email: {email_label}")
    print(f"   Risk Score : {report.risk_score}/100")
    print(f"   Risk Level : {report.risk_level}")
    print(f"   Intent     : {report.intent}")
    print(f"\n   📊 Analyzer Scores:")
    for name, score in report.analyzer_scores.items():
        print(f"      {name:>12}: {score:.1f}")
    print(f"\n   📝 Summary: {report.explanation_summary}")
    print(f"\n   🔎 Findings ({len(report.findings)}):")
    for i, f in enumerate(report.findings, 1):
        print(f"      {i}. [{f.analyzer}] {f.indicator}")
        print(f"         Score: +{f.score:.1f} | Evidence: {f.evidence[:80]}")
        print(f"         → {f.explanation[:100]}...")
    print(f"\n   💡 Tips ({len(report.awareness_tips)}):")
    for tip in report.awareness_tips:
        print(f"      • {tip[:120]}")


def test_phishing_email():
    """Test with a highly suspicious phishing email."""
    separator("TEST 1: Obvious Phishing Email")

    email = EmailData(
        subject="URGENT: Your Account Has Been Suspended!!!",
        sender_raw='"PayPal Security Team" <security-alert@free-mail-random.com>',
        body_text=(
            "Dear Customer, "
            "We detected unauthorized access to your PayPal account. "
            "Your account has been suspended due to suspicious activity. "
            "You must verify your account immediately or it will be closed within 24 hours. "
            "Click here to reset your password: http://192.168.1.100/paypal-verify "
            "Please provide your username, password, and credit card number to confirm your identity. "
            "Act now! Don't delay!!! "
            "Final warning — failure to respond will result in permanent account termination."
        ),
        body_html=(
            '<p>Dear Customer,</p>'
            '<p>Click <a href="http://192.168.1.100/paypal-verify">https://www.paypal.com/verify</a> '
            'to restore access.</p>'
            '<p>Or visit <a href="http://bit.ly/susp1cious">our security page</a>.</p>'
        ),
        date="Wed, 11 Feb 2026 10:00:00 +0000",
        message_id="test-phishing-001",
    )

    findings = analyze_email(email)
    report = generate_report(findings)
    print_report(report, "Obvious Phishing")

    assert report.risk_level == "High", f"Expected High risk, got {report.risk_level}"
    assert report.risk_score >= 50, f"Expected score >= 50, got {report.risk_score}"
    assert report.intent != "Legitimate", f"Expected non-Legitimate intent, got {report.intent}"
    assert len(report.findings) > 0, "Expected findings"
    print("\n   ✅ TEST 1 PASSED")
    return True


def test_legitimate_email():
    """Test with a normal, legitimate email."""
    separator("TEST 2: Legitimate Email")

    email = EmailData(
        subject="Meeting notes from today's standup",
        sender_raw='"Jane Smith" <jane.smith@acme-corp.com>',
        body_text=(
            "Hi Team,\n\n"
            "Here are the notes from today's standup meeting:\n\n"
            "1. Sprint review is scheduled for Friday at 2 PM.\n"
            "2. The new feature branch has been merged.\n"
            "3. Please update your Jira tickets by end of day.\n\n"
            "Thanks,\nJane Smith\nEngineering Manager, Acme Corp"
        ),
        body_html="",
        date="Wed, 11 Feb 2026 09:30:00 +0000",
        message_id="test-legit-001",
    )

    findings = analyze_email(email)
    report = generate_report(findings)
    print_report(report, "Legitimate Email")

    assert report.risk_level == "Low", f"Expected Low risk, got {report.risk_level}"
    assert report.risk_score <= 33, f"Expected score <= 33, got {report.risk_score}"
    assert report.intent == "Legitimate", f"Expected Legitimate intent, got {report.intent}"
    print("\n   ✅ TEST 2 PASSED")
    return True


def test_medium_risk_email():
    """Test with a moderately suspicious email."""
    separator("TEST 3: Medium-Risk Email")

    email = EmailData(
        subject="Update your account information",
        sender_raw='"Amazon Support" <support@amazzon-alerts.com>',
        body_text=(
            "Dear valued customer,\n\n"
            "We need you to update your information for your recent order. "
            "Please click the link below to verify your account details.\n\n"
            "https://amazzon-alerts.com/verify?user=12345\n\n"
            "Thank you,\nCustomer Support"
        ),
        body_html="",
        date="Wed, 11 Feb 2026 08:00:00 +0000",
        message_id="test-medium-001",
    )

    findings = analyze_email(email)
    report = generate_report(findings)
    print_report(report, "Medium-Risk Email")

    assert report.risk_score > 10, f"Expected score > 10, got {report.risk_score}"
    assert len(report.findings) > 0, "Expected some findings"
    print("\n   ✅ TEST 3 PASSED")
    return True


def test_malware_email():
    """Test with a malware-delivery email."""
    separator("TEST 4: Malware Delivery Email")

    email = EmailData(
        subject="Invoice #38291 — Please Review",
        sender_raw='"Accounting Dept" <invoices@gmail.com>',
        body_text=(
            "Dear Sir/Madam,\n\n"
            "Please find attached the invoice for your recent purchase. "
            "Download the attachment and enable macros to view the document. "
            "Open the attached file immediately. "
            "This is urgent and requires your immediate attention.\n\n"
            "Regards,\nAccounting Department"
        ),
        body_html=(
            '<p>Download: <a href="http://bit.ly/m4lware-doc">Invoice_38291.docm</a></p>'
        ),
        date="Wed, 11 Feb 2026 07:15:00 +0000",
        message_id="test-malware-001",
    )

    findings = analyze_email(email)
    report = generate_report(findings)
    print_report(report, "Malware Delivery Email")

    assert report.risk_score >= 30, f"Expected score >= 30, got {report.risk_score}"
    assert len(report.findings) >= 3, f"Expected >= 3 findings, got {len(report.findings)}"
    print("\n   ✅ TEST 4 PASSED")
    return True


def test_url_analysis():
    """Test URL-focused detection."""
    separator("TEST 5: URL-Heavy Email")

    email = EmailData(
        subject="Check out this link",
        sender_raw="someone@example.com",
        body_text=(
            "Hey, look at this: http://192.168.0.1/free-stuff "
            "Also try: http://login.secure.bank.evil-site.com/steal "
        ),
        body_html=(
            '<a href="http://evil.com/phish">https://www.google.com/safe</a>'
        ),
        date="Wed, 11 Feb 2026 06:00:00 +0000",
        message_id="test-url-001",
    )

    findings = analyze_email(email)
    report = generate_report(findings)
    print_report(report, "URL-Heavy Email")

    url_findings = [f for f in report.findings if f.analyzer == "url"]
    assert len(url_findings) >= 2, f"Expected >= 2 URL findings, got {len(url_findings)}"
    print("\n   ✅ TEST 5 PASSED")
    return True


if __name__ == "__main__":
    separator("PHISHING ENGINE TEST SUITE")
    print("Running 5 test scenarios against the detection engine...\n")

    results = []
    results.append(("Test 1: Obvious Phishing", test_phishing_email()))
    results.append(("Test 2: Legitimate Email", test_legitimate_email()))
    results.append(("Test 3: Medium-Risk Email", test_medium_risk_email()))
    results.append(("Test 4: Malware Delivery", test_malware_email()))
    results.append(("Test 5: URL Analysis", test_url_analysis()))

    separator("TEST RESULTS SUMMARY")
    all_passed = True
    for name, passed in results:
        status = "✅ PASS" if passed else "❌ FAIL"
        print(f"   {status}  {name}")
        if not passed:
            all_passed = False

    print(f"\n{'═' * 70}")
    if all_passed:
        print("   🎉 ALL 5 TESTS PASSED — Engine is working correctly!")
    else:
        print("   ⚠️  Some tests failed. Review the output above.")
    print(f"{'═' * 70}\n")

    sys.exit(0 if all_passed else 1)

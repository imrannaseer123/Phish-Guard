import sys
import os

# Ensure we can import from the current directory
sys.path.append(os.getcwd())

from phishing_engine import Finding, EmailData
import header_forensics

def test_header_analysis():
    print("Testing Header Forensics...")
    
    # 1. Test SPF Fail
    email1 = EmailData(sender_raw="attacker@bad.com")
    email1.headers = {
        "Authentication-Results": "spf=fail (sender IP is 1.2.3.4)",
        "Received-SPF": "fail (domain of bad.com does not designate 1.2.3.4 as permitted sender)"
    }
    findings1 = header_forensics.analyze_headers(email1)
    print(f"Test 1 (SPF Fail): Found {len(findings1)} issues.")
    if any(f.indicator == "spf_fail" for f in findings1):
        print("  [PASS] SPF Fail detected.")
    else:
        print("  [FAIL] SPF Fail NOT detected.")

    # 2. Test Domain Mismatch
    email2 = EmailData(sender_raw="ceo@company.com")
    email2.headers = {
        "Return-Path": "<mailer@bulk-spam-service.com>",
        "Authentication-Results": "spf=pass"
    }
    findings2 = header_forensics.analyze_headers(email2)
    print(f"Test 2 (Routing): Found {len(findings2)} issues.")
    if any(f.indicator == "domain_mismatch" for f in findings2):
        print("  [PASS] Domain Mismatch detected.")
    else:
        print("  [FAIL] Domain Mismatch NOT detected.")

    # 3. Test Clean Email
    email3 = EmailData(sender_raw="support@google.com")
    email3.headers = {
        "Return-Path": "<support@google.com>",
        "Authentication-Results": "mx.google.com; dk=pass; spf=pass"
    }
    findings3 = header_forensics.analyze_headers(email3)
    print(f"Test 3 (Clean): Found {len(findings3)} issues.")
    if len(findings3) == 0:
        print("  [PASS] No findings for clean email.")
    else:
        print(f"  [FAIL] Found issues for clean email: {findings3}")

if __name__ == "__main__":
    test_header_analysis()

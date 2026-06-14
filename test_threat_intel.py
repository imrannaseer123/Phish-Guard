
import sys
import os
from dataclasses import dataclass, field

# Ensure we can import from the current directory
sys.path.append(os.getcwd())

import config
import phishing_engine

def test_threat_intel():
    print("Testing External Threat Intelligence (Feature 6)...")
    
    # 1. Create a dummy email with a known malicious URL
    # "apple-id-reset.tk" is in our mock blacklist in threat_intel.py
    malicious_url = "http://apple-id-reset.tk/login"
    
    email = phishing_engine.EmailData(
        subject="Action Required",
        sender_raw="support@apple.com",
        body_text=f"Please verify your ID here: {malicious_url}"
    )
    
    # 2. Run Analysis
    print(f"Analyzing email with URL: {malicious_url}")
    findings = phishing_engine.analyze_email(email)
    
    # 3. Check for Threat Intel Finding
    ti_finding = None
    for f in findings:
        if f.analyzer == "threat_intel" and f.indicator == "known_malicious_url":
            ti_finding = f
            break
            
    if ti_finding:
        print(f"[PASS] Detected malicious URL: {ti_finding.evidence}")
        print(f"       Score: {ti_finding.score}")
        print(f"       Explanation: {ti_finding.explanation}")
    else:
        print("[FAIL] Threat Intel analyzer did not flag the URL.")
        print("Findings found:")
        for f in findings:
            print(f" - [{f.analyzer}] {f.indicator}")

if __name__ == "__main__":
    try:
        test_threat_intel()
    except Exception as e:
        print(f"Test FAILED: {e}")
        import traceback
        traceback.print_exc()

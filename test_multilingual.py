
import sys
import os
from dataclasses import dataclass, field

# Ensure we can import from the current directory
sys.path.append(os.getcwd())

import config
import multilingual
import phishing_engine

def test_multilingual_flow():
    print("Testing Multilingual Phishing Detection...")
    
    # 1. Create a dummy Spanish phishing email
    # "Urgent: Update your account immediately. Click here to login."
    spanish_text = "Urgente: Actualice su cuenta inmediatamente. Haga clic aquí para iniciar sesión."
    
    email = phishing_engine.EmailData(
        subject="Alerta de Seguridad",
        sender_raw="soporte@banco-falso.com",
        body_text=spanish_text
    )
    
    # 2. Test Detection & Translation Code directly
    print(f"Original Text: {email.body_text}")
    multilingual.analyze_language(email)
    
    print(f"Detected Language: {email.language}")
    print(f"Translated Body: {email.translated_body}")
    
    if email.language == 'en':
        print("[WARN] Language detection might have defaulted to 'en' (text too short?).")
    
    # 3. Test Engine Integration
    # The engine should use the translated body to find keywords like "urgent", "click here", "login"
    print("\nRunning Full Analysis...")
    findings = phishing_engine.analyze_email(email)
    
    # Check for specific indicators that define success
    # "Urgente" -> "Urgent" (Urgency Analyzer)
    # "Haga clic aquí" -> "Click here" (Keyword Analyzer)
    
    found_urgency = any(f.indicator == "urgency_phrase" for f in findings)
    found_keyword = any(f.indicator == "suspicious_keyword" for f in findings)
    
    print(f"Findings Count: {len(findings)}")
    for f in findings:
        print(f" - [{f.analyzer}] {f.indicator}: {f.score} p")
        
    if found_urgency or found_keyword:
        print("[PASS] Multilingual analysis detected threats in translated text.")
    else:
        print("[FAIL] No threats detected. Translation might have failed or keywords didn't match.")

if __name__ == "__main__":
    try:
        if not config.GEMINI_API_KEY:
            print("[SKIP] No GEMINI_API_KEY found in config. Skipping test.")
        else:
            test_multilingual_flow()
    except Exception as e:
        print(f"Test FAILED: {e}")
        import traceback
        traceback.print_exc()

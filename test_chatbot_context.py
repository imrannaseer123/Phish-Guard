
import sys
import os

# Ensure we can import from the current directory
sys.path.append(os.getcwd())

import config
import chatbot_service

def test_chatbot_context():
    print("Testing Chatbot Context Injection (Feature 7)...")
    
    # 1. Simulate findings from all new analyzers
    mock_findings = [
        {'analyzer': 'qr_analyzer', 'indicator': 'malicious_qr', 'evidence': 'http://evil.com/qr'},
        {'analyzer': 'ocr_analyzer', 'indicator': 'suspicious_text', 'evidence': 'URGENT: WIRE TRANSFER'},
        {'analyzer': 'header_forensics', 'indicator': 'spf_fail', 'evidence': 'SoftFail'},
        {'analyzer': 'threat_intel', 'indicator': 'known_malicious_url', 'evidence': 'http://apple-id-reset.tk'}
    ]
    
    mock_context = {
        'risk_score': 85,
        'findings': mock_findings
    }
    
    # 2. Ask a question that requires context
    question = "Can you explain why this email is dangerous?"
    print(f"\nUser Question: {question}")
    
    # 3. Process
    result = chatbot_service.process_message(question, mock_context)
    
    print(f"\nSource: {result['source']}")
    print(f"Response:\n{result['response']}")
    
    # Basic validation
    if result['source'] == "System Warning":
        print("[SKIP] API Key missing, cannot verify AI response content.")
    elif "error" in result['response'].lower():
        print("[FAIL] Chatbot returned an error.")
    else:
        print("[PASS] Chatbot generated a response using the provided context.")

if __name__ == "__main__":
    try:
        test_chatbot_context()
    except Exception as e:
        print(f"Test FAILED: {e}")
        import traceback
        traceback.print_exc()

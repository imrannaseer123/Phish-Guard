import sys
import os
import base64
import cv2
import numpy as np

# Ensure we can import from the current directory
sys.path.append(os.getcwd())

import phishing_engine
from phishing_engine import EmailData, analyze_email

def create_qr_code_image(data="http://malicious-site.com"):
    # Create a simple QR code using qrcode library if available, but we didn't install it.
    # So we will use a pre-calculated base64 of a QR code or just mock the qr_analyzer response if needed.
    # BUT, we want to test the integration.
    # Since we can't easily generate a QR code without `qrcode` lib, let's mock the qr_analyzer.scan_qr_codes 
    # OR we can assume the dependencies work if we can just import them.
    
    # Better: let's test the imports and the logic flow.
    print("Testing imports...")
    import qr_analyzer
    import ocr_analyzer
    print("Imports successful.")
    
    # Mock Email with an attachment that CLAIMS to be an image
    # We will pass a dummy image (black square) to see if it crashes or handles it.
    
    # Create a small black image
    img = np.zeros((100, 100, 3), dtype=np.uint8)
    _, buffer = cv2.imencode(".png", img)
    img_bytes = buffer.tobytes()
    
    email = EmailData(
        subject="Test QR",
        body_text="Look at this",
        attachments=[{
            "filename": "test.png",
            "mime_type": "image/png",
            "data": img_bytes
        }]
    )
    
    print("Running analysis...")
    findings = analyze_email(email)
    print(f"Analysis complete. Findings: {len(findings)}")
    for f in findings:
        print(f"- {f.indicator}: {f.score}")

    # Note: We won't find a QR code in a black square, but if it runs without error, the integration is successful.
    print("Test passed IF no crash occurred.")

if __name__ == "__main__":
    try:
        create_qr_code_image()
    except Exception as e:
        print(f"Test FAILED: {e}")
        import traceback
        traceback.print_exc()

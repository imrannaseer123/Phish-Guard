import logging
import io
try:
    from PIL import Image
    import pytesseract
    PIL_AVAILABLE = True
except ImportError:
    PIL_AVAILABLE = False
    print("WARNING: Pillow or pytesseract not installed. OCR analysis will be skipped.")

# from phishing_engine import Finding

def extract_text_from_image(image_bytes: bytes, filename: str) -> str:
    """
    Extract text from an image using OCR.
    Returns the extracted string or empty string on failure.
    """
    text = ""
    if not PIL_AVAILABLE:
        return text

    try:
        image = Image.open(io.BytesIO(image_bytes))
        # Tesseract execution
        text = pytesseract.image_to_string(image)
    except Exception as e:
        # Verify if Tesseract is installed; often fails if binary not in PATH
        if "tesseract is not installed" in str(e).lower():
            logging.warning("Tesseract OCR binary not found. Please install Tesseract-OCR.")
        else:
            logging.error(f"OCR failed for {filename}: {e}")
    
    return text

def analyze_ocr_text(text: str, filename: str) -> list:
    """
    Analyze the extracted text for phishing indicators.
    """
    from phishing_engine import Finding
    findings = []
    if not text.strip():
        return findings

    # Simple Keyword Check (Re-implementing basic check to tackle image-text)
    # In a real scenario, we'd import the keyword analyzer, but let's keep it self-contained to avoid circular imports if structured poorly.
    
    suspicious_keywords = ["urgent", "verify", "account", "suspended", "login", "password", "bank", "security alert"]
    
    found_keywords = []
    for kw in suspicious_keywords:
        if kw in text.lower():
            found_keywords.append(kw)
    
    if found_keywords:
        findings.append(Finding(
            analyzer="ocr_image",
            indicator="hidden_text_phishing",
            score=20.0,
            evidence=f"Hidden text in {filename}: {', '.join(found_keywords)}",
            explanation=(
                f"The image '{filename}' contains suspicious text ({', '.join(found_keywords)}) "
                f"that is often found in phishing emails. Attackers use images to hide text from spam filters."
            )
        ))
        
    return findings

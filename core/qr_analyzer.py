try:
    import cv2
    import numpy as np
    from pyzbar.pyzbar import decode
    OPENCV_AVAILABLE = True
except (ImportError, FileNotFoundError, Exception) as e:
    OPENCV_AVAILABLE = False
    print(f"WARNING: QR Code dependencies missing ({e}). QR analysis will be skipped.")

# from phishing_engine import Finding (Circular import fix: moved inside function)

def scan_qr_codes(image_bytes: bytes, filename: str) -> list:
    """
    Scan an image (from bytes) for QR codes and return findings.
    """
    from phishing_engine import Finding
    findings = []
    
    if not OPENCV_AVAILABLE:
        return findings

    try:
        # Convert bytes to numpy array for OpenCV
        nparr = np.frombuffer(image_bytes, np.uint8)
        img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)

        if img is None:
            logging.warning(f"Failed to decode image: {filename}")
            return findings

        # Detect and decode
        decoded_objects = decode(img)
        
        for obj in decoded_objects:
            url = obj.data.decode("utf-8")
            
            findings.append(Finding(
                analyzer="qr_code",
                indicator="qr_code_detected",
                score=15.0,  # Base score for just having a QR code
                evidence=f"QR Code in {filename} -> {url}",
                explanation=(
                    f"A QR code was detected in the attachment '{filename}'. "
                    f"Attackers use QR codes (Quishing) to bypass email filters. "
                    f"Verify the destination URL carefully: {url}"
                )
            ))
            
            # TODO: Recursively analyze this URL using the URL analyzer
            # For now, we just flag the QR code itself.
            
    except Exception as e:
        logging.error(f"Error scanning QR code in {filename}: {e}")

    return findings

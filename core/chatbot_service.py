import re

import google.generativeai as genai
import config

# Configure Gemini API if key is present
if config.GEMINI_API_KEY:
    genai.configure(api_key=config.GEMINI_API_KEY)


def _redact_pii(text: str) -> str:
    """
    Redact potential PII from text before AI processing.
    Removes emails, phone numbers, credit card numbers, and SSN-like sequences.
    """
    if not text:
        return ""
    text = re.sub(r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}', '[REDACTED_EMAIL]', text)
    text = re.sub(r'\b(?:\+\d{1,3}[- ]?)?\(?\d{3}\)?[- ]?\d{3}[- ]?\d{4}\b', '[REDACTED_PHONE]', text)
    text = re.sub(r'\b(?:\d[ -]*?){13,16}\b', '[REDACTED_CC]', text)
    text = re.sub(r'\b\d{3}-\d{2}-\d{4}\b', '[REDACTED_SSN]', text)
    return text


def process_message(user_message: str, context: dict = None) -> dict:
    """
    Process a user message using Gemini 1.5 Pro for intelligent responses.
    
    Args:
        user_message (str): The raw input from the user.
        context (dict): Optional context (e.g., current report ID, risk score, findings).
        
    Returns:
        dict: Response containing 'response' text and 'source'.
    """
    if not user_message:
        return {"response": "I didn't catch that. How can I help you with email security?", "source": "System"}

    # 1. Privacy First: Redact PII
    try:
        safe_message = _redact_pii(user_message)
    except Exception as e:
        print(f"Redaction failed: {e}")
        safe_message = user_message  # Fallback

    # 2. Check for API Key
    if not config.GEMINI_API_KEY:
        return {
            "response": "I'm currently running in offline mode because the AI API key is missing. Please configure 'GEMINI_API_KEY' in config.py to unlock my full potential.",
            "source": "System Warning"
        }

    try:
        # 3. Construct System Prompt
        system_instruction = """
        You are a cybersecurity assistant for the PhishGuard phishing detection system.
        
        RULES:
        - Answer ONLY the user's question.
        - Do NOT repeat generic phishing definitions unless asked.
        - If context is provided, reference specific indicators (risk score, findings).
        - Be specific, concise, and advisory.
        - Do NOT make final decisions (e.g., "Delete this now"). Instead say "I recommend caution..."
        
        EXPLAINING FINDINGS:
        - **QR Codes**: Explain that attackers use them to hide malicious URLs from scanners.
        - **OCR/Images**: Explain that text inside images is used to bypass text filters.
        - **Headers (SPF/DKIM)**: Explain that these are identity checks. specific failures mean the sender might be spoofed.
        - **Threat Intel**: Mention if a URL is on a known blacklist (VirusTotal/Google Safe Browsing).
        
        TONE:
        - Professional, helpful, and vigilant.
        """
        
        # 4. Build Context String
        context_str = ""
        if context:
            score = context.get('risk_score')
            if score is not None:
                context_str += f"Current Email Risk Score: {score}/100.\n"
            
            findings = context.get('findings', [])
            if findings:
                context_str += "Detected Indicators:\n"
                for f in findings:
                    # Handle both dictionary and object access if necessary, assuming dict from app.py
                    if isinstance(f, dict):
                        analyzer = f.get('analyzer', 'unknown')
                        indicator = f.get('indicator', 'unknown')
                        evidence = f.get('evidence', '')
                        context_str += f"- [{analyzer}] {indicator}: {evidence}\n"
        
        # 5. Generate Content
        model = genai.GenerativeModel(config.CHATBOT_MODEL)
        
        full_prompt = f"{system_instruction}\n\nCONTEXT:\n{context_str}\n\nUSER QUESTION:\n{safe_message}\n\nINSTRUCTION:\nGenerate a clear, original response tailored to this question."
        
        response = model.generate_content(full_prompt)
        
        return {
            "response": response.text,
            "source": f"Gemini ({config.CHATBOT_MODEL})"
        }

    except Exception as e:
        print(f"Gemini API Error: {e}")
        return {
            "response": "I'm having trouble connecting to my AI brain right now. Please try again later.",
            "source": "System Error"
        }

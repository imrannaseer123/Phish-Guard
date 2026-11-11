
import logging
from langdetect import detect, LangDetectException
import google.generativeai as genai
import config

# Configure Gemini API
if config.GEMINI_API_KEY:
    genai.configure(api_key=config.GEMINI_API_KEY)

def detect_language(text: str) -> str:
    """
    Detect the language of the text.
    Returns ISO 639-1 language code (e.g., 'en', 'es').
    Defaults to 'en' on failure or short text.
    """
    if not text or len(text.strip()) < 10:
        return 'en'
    
    try:
        return detect(text)
    except LangDetectException:
        return 'en'
    except Exception as e:
        print(f"Language detection failed: {e}")
        return 'en'

def translate_body(text: str) -> str:
    """
    Translate text to English using Gemini API.
    Returns the translated text or empty string on failure.
    """
    if not config.GEMINI_API_KEY:
        print("Skipping translation: No API key.")
        return ""
        
    try:
        # Use a cost-effective model for translation
        model_name = getattr(config, 'CHATBOT_MODEL', 'gemini-1.5-flash')
        model = genai.GenerativeModel(model_name)
        
        prompt = (
            "Translate the following email content into English. "
            "Return ONLY the translated text, do not add any preamble or explanation.\n\n"
            f"{text[:5000]}" # Truncate to avoid token limits/costs on very large emails
        )
        
        response = model.generate_content(prompt)
        if response and response.text:
            return response.text.strip()
            
    except Exception as e:
        print(f"Translation failed: {e}")
        
    return ""

def analyze_language(email_data):
    """
    Detect language and translate if necessary.
    Updates email_data in-place with 'language' and 'translated_body'.
    """
    # Prefer body_text, fallback to stripped HTML if needed (but email_data usually has text)
    content = email_data.body_text
    
    if not content:
        return

    lang = detect_language(content)
    email_data.language = lang
    
    if lang != 'en':
        print(f"Non-English content detected ({lang}). Translating...")
        translated = translate_body(content)
        if translated:
            email_data.translated_body = translated
            print("Translation successful.")

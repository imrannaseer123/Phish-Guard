import os
import sys

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

import google.generativeai as genai
import config

def test_gemini():
    print(f"Using API Key: {config.GEMINI_API_KEY[:5]}...{config.GEMINI_API_KEY[-5:]}")
    genai.configure(api_key=config.GEMINI_API_KEY)
    
    try:
        model = genai.GenerativeModel("gemini-flash-latest")
        response = model.generate_content("Hello, are you working?")
        print("Success!")
        print(response.text)
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    test_gemini()

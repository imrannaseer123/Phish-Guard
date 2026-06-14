import requests
import json

def test_chatbot():
    url = "http://localhost:5000/chatbot/message"
    payload = {
        "message": "What is my risk score?",
        "context": {"risk_score": 75}
    }
    headers = {"Content-Type": "application/json"}

    try:
        response = requests.post(url, json=payload, headers=headers)
        print(f"Status Code: {response.status_code}")
        data = response.json()
        print(f"Source: {data.get('source')}")
        print("Response JSON:")
        print(json.dumps(data, indent=2))
    except Exception as e:
        print(f"Request failed: {e}")

if __name__ == "__main__":
    test_chatbot()

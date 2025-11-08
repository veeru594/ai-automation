import os, requests
from dotenv import load_dotenv

load_dotenv()
api_key = os.getenv("GEMINI_API_KEY")

url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent?key={api_key}"

prompt = {
    "contents": [{"parts": [{"text": "Give one line about current digital marketing trends"}]}]
}

r = requests.post(url, json=prompt)
try:
    print(r.json()["candidates"][0]["content"]["parts"][0]["text"])
except Exception as e:
    print("Error:", r.text)

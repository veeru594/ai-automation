import requests
from ai_brain.config import GEMINI_API_KEY

def extract_text_from_gemini(result):
    """
    Safely extracts text from Gemini API responses.
    Works for all known versions (1.5, 2.0, 2.5).
    """
    try:
        # Standard Gemini response
        if "candidates" in result:
            for candidate in result["candidates"]:
                if "content" in candidate and "parts" in candidate["content"]:
                    for part in candidate["content"]["parts"]:
                        if "text" in part:
                            return part["text"].strip()

        # Alternate Gemini response keys
        if "output" in result:
            return result["output"]
        if "text" in result:
            return result["text"]

        # Fallback: partial JSON for debugging
        import json
        return f"[Unexpected Response Format]\n{json.dumps(result, indent=2)[:300]}"

    except Exception as e:
        return f"[Error extracting text: {e}]"


def generate_post(topic, tone="Professional"):
    """
    Generates a short, creative post about a given topic using Gemini API.
    """
    if not GEMINI_API_KEY:
        return f"[Mock Output] Post about: {topic}"

    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent?key={GEMINI_API_KEY}"
    headers = {"Content-Type": "application/json"}
    data = {
        "contents": [
            {
                "parts": [
                    {
                        "text": (
                            f"Write a short, {tone.lower()} LinkedIn post (under 80 words) "
                            f"about '{topic}'. Focus on clarity, creativity, and engagement."
                        )
                    }
                ]
            }
        ]
    }

    try:
        response = requests.post(url, headers=headers, json=data)
        result = response.json()

        # Uncomment to debug raw Gemini output
        # print("DEBUG RAW RESPONSE:", result)

        # Handle HTTP errors
        if response.status_code != 200:
            message = result.get("error", {}).get("message", "Unknown error")
            return f"[Error] Gemini API returned {response.status_code}: {message}"

        return extract_text_from_gemini(result)

    except Exception as e:
        return f"[Error] Gemini request failed: {e}"

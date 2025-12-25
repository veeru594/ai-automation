import json
import requests
from ai_brain.config import GROQ_API_KEY, GROQ_URL

def _clean_json(raw: str) -> str:
    if not isinstance(raw, str):
        return raw
    return raw.strip().replace("```json", "").replace("```", "").strip()


def generate_three_news_prompts(news_items):
    """
    Accepts list of 3 SERP news dicts:
    [{title: "...", snippet: "..."}, ...]

    Returns:
    {
      "slides": [
        {"slide":2, "headline":"...", "insight":"..."},
        {"slide":3, "headline":"...", "insight":"..."},
        {"slide":4, "headline":"...", "insight":"..."}
      ]
    }
    """

    if not GROQ_API_KEY:
        return {
            "slides": [
                {"slide": 2, "headline": "AI Boosts Marketing Automation Efficiency", "insight": "Brands gain faster workflows with improved AI tools."},
                {"slide": 3, "headline": "Instagram Tests Smarter Content Ranking System", "insight": "Creators may see improved engagement with algorithm updates."},
                {"slide": 4, "headline": "Google Adds Insights To Search Console Tools", "insight": "Marketers get clearer visibility into ranking changes."}
            ]
        }

    # Build GROQ prompt
    prompt = f"""
You will receive 3 REAL NEWS ITEMS fetched from Google News (SERP).

Rewrite each item into a clean, professional Instagram news slide.

RULES:
- Each item becomes ONE slide only.
- Headline must be 6–10 words, punchy, factual, not clickbait.
- Insight must be a single sentence (12–20 words) explaining why the update matters.
- No invented facts.
- Keep it concise, neutral, and industry-relevant.
- Output valid JSON only.

INPUT NEWS:
1. Title: {news_items[0]["title"]}
   Summary: {news_items[0]["snippet"]}

2. Title: {news_items[1]["title"]}
   Summary: {news_items[1]["snippet"]}

3. Title: {news_items[2]["title"]}
   Summary: {news_items[2]["snippet"]}

OUTPUT FORMAT:
{{
  "slides": [
    {{ "slide": 2, "headline": "", "insight": "" }},
    {{ "slide": 3, "headline": "", "insight": "" }},
    {{ "slide": 4, "headline": "", "insight": "" }}
  ]
}}
"""

    headers = {
        "Authorization": f"Bearer {GROQ_API_KEY}",
        "Content-Type": "application/json"
    }

    payload = {
        "model": "llama-3.3-70b-versatile",
        "messages": [{"role": "user", "content": prompt}],
        "temperature": 0.2
    }

    try:
        r = requests.post(GROQ_URL, headers=headers, json=payload, timeout=30)
        data = r.json()
    except Exception as e:
        return {"error": f"Groq request failed: {e}"}

    raw = data["choices"][0]["message"]["content"]
    raw = _clean_json(raw)

    try:
        return json.loads(raw)
    except:
        try:
            start = raw.index("{")
            end = raw.rindex("}") + 1
            return json.loads(raw[start:end])
        except Exception as e:
            return {"error": "Failed to parse Groq JSON", "raw": raw, "err": str(e)}

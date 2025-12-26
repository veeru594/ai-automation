import json
import requests
from ai_brain.config import GROQ_API_KEY, GROQ_URL


def evaluate_news(news_items, posted_titles):
    """
    Editorial gatekeeper: decide what is REAL + WORTH POSTING.
    
    Input:
    - news_items: list from trend_fetcher (raw signals)
    - posted_titles: list of previously posted normalized titles
    
    Output schema:
    {
        "approved": [
            {
                "entity": str,
                "category": str,  # platform | ads | seo | privacy | commerce | creator_monetization
                "summary": str,   # Factual one-line description
                "marketer_impact": str,  # Why this matters (practical)
                "confidence": str  # "confirmed"
            }
        ],
        "rejected": [
            {
                "title": str,
                "reason": str  # duplicate | opinion | recap | low_impact
            }
        ]
    }
    """
    
    if not news_items:
        return {"approved": [], "rejected": []}
    
    news_block = "\n".join(
        f"- {n['title']} ({n['source']})"
        for n in news_items
    )
    
    posted_block = "\n".join(posted_titles) if posted_titles else "(none)"
    
    prompt = f"""You are a senior tech & digital marketing news editor.

You will receive REAL, RECENT platform announcements.
Your job is to decide which are worth publishing today.

STRICT RULES:
- Use ONLY the provided input.
- DO NOT invent or replace news.
- Reject opinion, recap, or duplicate updates.
- If nothing is strong enough, approve nothing.

Previously posted headlines (avoid repetition):
{posted_block}

INPUT NEWS:
{news_block}

For each APPROVED item, return:
- entity
- category: platform | ads | seo | privacy | commerce | creator_monetization
- summary: factual one-line description
- marketer_impact: why this matters (practical)
- confidence: confirmed

Return valid JSON only.

FORMAT:
{{
  "approved": [
    {{
      "entity": "...",
      "category": "...",
      "summary": "...",
      "marketer_impact": "...",
      "confidence": "confirmed"
    }}
  ],
  "rejected": [
    {{
      "title": "...",
      "reason": "duplicate | opinion | recap | low_impact"
    }}
  ]
}}
"""
    
    payload = {
        "model": "llama-3.3-70b-versatile",
        "messages": [{"role": "user", "content": prompt}],
        "temperature": 0.1
    }
    
    headers = {
        "Authorization": f"Bearer {GROQ_API_KEY}",
        "Content-Type": "application/json"
    }
    
    try:
        r = requests.post(GROQ_URL, headers=headers, json=payload, timeout=30)
        raw = r.json()["choices"][0]["message"]["content"]
        raw = raw.strip().replace("```json", "").replace("```", "")
        return json.loads(raw)
    except Exception as e:
        return {
            "approved": [],
            "rejected": [],
            "error": str(e)
        }

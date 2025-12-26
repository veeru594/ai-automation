import json
import requests
from ai_brain.config import GROQ_API_KEY, GROQ_URL

def _clean_json(raw: str) -> str:
    if not isinstance(raw, str):
        return raw
    return raw.strip().replace("```json", "").replace("```", "").strip()


def evaluate_and_summarize(news_items):
    """
    Editorial gatekeeper: approve or reject news signals.
    
    Input schema (from trend_fetcher):
    [
        {
            "entity": str,
            "title": str,
            "snippet": str,
            "source": str,
            "url": str
        }
    ]
    
    Output schema:
    {
        "approved": [
            {
                "entity": str,              # Platform/company name
                "update_type": str,         # "feature_release" | "algorithm_change" | "policy_update"
                "summary": str,             # One sentence factual summary
                "takeaway": str,            # Tactical implication (20-25 words)
                "confidence": str           # "confirmed" | "reported" | "rumored"
            }
        ],
        "rejected": [
            {
                "title": str,
                "reason": str               # Why it was rejected
            }
        ]
    }
    """
    
    if not GROQ_API_KEY:
        # Fallback: minimal approved set
        return {
            "approved": [
                {
                    "entity": "Instagram",
                    "update_type": "feature_release",
                    "summary": "Instagram expands Reels to 10 minutes",
                    "takeaway": "Creators can now publish longer-form content without external platforms",
                    "confidence": "confirmed"
                }
            ],
            "rejected": []
        }

    # Build editorial prompt
    prompt = f"""You are an editorial gatekeeper for a tech marketing news channel.

INPUT: {len(news_items)} news signals from SERP.

TASK: Classify each as APPROVED or REJECTED.

APPROVAL CRITERIA:
- Specific feature launches, algorithm updates, or policy changes
- Confirmed by credible source
- Relevant to digital marketers

REJECTION CRITERIA:
- Opinion pieces, predictions, or "Top 10" lists
- Generic trends without specific updates
- Speculative or unconfirmed rumors

INPUT NEWS:
"""
    
    for i, item in enumerate(news_items, 1):
        prompt += f"{i}. Entity: {item.get('entity', 'Unknown')}\n"
        prompt += f"   Title: {item.get('title', '')}\n"
        prompt += f"   Snippet: {item.get('snippet', '')}\n"
        prompt += f"   Source: {item.get('source', '')}\n\n"
    
    prompt += """
OUTPUT RULES:
- If a signal is weak/speculative, REJECT it with reason
- Do NOT invent updates that aren't in the input
- Classify update_type as: "feature_release", "algorithm_change", or "policy_update"
- Confidence: "confirmed" (official announcement), "reported" (credible journalism), "rumored" (unverified)

OUTPUT FORMAT (valid JSON only):
{
  "approved": [
    {
      "entity": "Platform Name",
      "update_type": "feature_release",
      "summary": "One sentence factual description",
      "takeaway": "Tactical implication for marketers (20-25 words)",
      "confidence": "confirmed"
    }
  ],
  "rejected": [
    {
      "title": "Original headline",
      "reason": "Specific reason for rejection"
    }
  ]
}
"""

    headers = {
        "Authorization": f"Bearer {GROQ_API_KEY}",
        "Content-Type": "application/json"
    }

    payload = {
        "model": "llama-3.3-70b-versatile",
        "messages": [{"role": "user", "content": prompt}],
        "temperature": 0.1  # Lower temp = more deterministic
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

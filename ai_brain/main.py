# ai_brain/main.py
import datetime
import json
import requests
from ai_brain.trend_fetcher import fetch_trending_topics
from ai_brain.gemini_generator import generate_post
from ai_brain.config import GEMINI_API_KEY

print("Gemini Key Loaded:", bool(GEMINI_API_KEY))


def create_posts():
    """
    Generates post content based on the current time (9 AM or 4 PM),
    fetching live trends via SerpAPI and generating creative posts via Gemini.
    """
    now = datetime.datetime.now()
    hour = now.hour

    # Morning session (9 AM): Live trending topics from SerpAPI
    if 5 <= hour < 12:
        category = "Morning Trends"
        print("☀️ Fetching live trends from SerpAPI...")
        topics = fetch_trending_topics(query="digital marketing trends", num_results=3)

    # Evening session (4 PM): Use-case based posts
    else:
        category = "Evening Use-Cases"
        print("🌇 Generating digital marketing use-case posts...")
        topics = [
            "How digital marketing helps small businesses",
            "Benefits of analytics in campaigns",
            "The future of social media automation"
        ]

    posts = []
    for topic in topics:
        print(f"🧠 Generating content for: {topic}")
        content = generate_post(topic, tone="Professional")
        posts.append({"topic": topic, "content": content})

    output = {
        "time": now.strftime("%H:%M"),
        "category": category,
        "posts": posts
    }

    # Log to console
    print("\n✅ Generated Output:")
    print(json.dumps(output, indent=2))
    return output


def send_to_n8n(data):
    """
    Sends the generated post data to your n8n webhook for further automation.
    """
    webhook_url = "https://veerandrakumar.app.n8n.cloud/webhook-test/0bd6a134-ba4e-4249-bab4-6dbdf99caf4d"
    try:
        response = requests.post(webhook_url, json=data)
        if response.status_code == 200:
            print("📡 Successfully sent data to n8n.")
        else:
            print(f"⚠️ n8n Webhook Error: {response.status_code} - {response.text}")
    except Exception as e:
        print("❌ Failed to send data to n8n:", e)


if __name__ == "__main__":
    data = create_posts()
    send_to_n8n(data)

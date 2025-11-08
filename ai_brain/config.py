import os
from dotenv import load_dotenv

# Locate .env in the parent folder
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ENV_PATH = os.path.join(BASE_DIR, ".env")

print(f"🔍 Searching for .env at: {ENV_PATH}")

if os.path.exists(ENV_PATH):
    load_dotenv(ENV_PATH, override=True)
    print("✅ .env file found and loaded.")
else:
    print("⚠️ .env file NOT found.")

# Show the first few chars of the key to confirm load
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
SERPAPI_KEY = os.getenv("SERPAPI_KEY")

if GEMINI_API_KEY:
    print("🔑 GEMINI_API_KEY Loaded: True →", GEMINI_API_KEY[:8] + "...")
else:
    print("🔑 GEMINI_API_KEY Loaded: False")

if SERPAPI_KEY:
    print("🔑 SERPAPI_KEY Loaded: True →", SERPAPI_KEY[:6] + "...")

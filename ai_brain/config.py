import os
from dotenv import load_dotenv

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ENV_PATH = os.path.join(BASE_DIR, ".env")
if os.path.exists(ENV_PATH):
    load_dotenv(ENV_PATH, override=True)

# Keys (set in .env)
GROQ_API_KEY = os.getenv("GROQ_API_KEY")
LEONARDO_API_KEY = os.getenv("LEONARDO_API_KEY")
SERPAPI_KEY = os.getenv("SERPAPI_KEY")

# Endpoints
GROQ_URL = "https://api.groq.com/openai/v1/chat/completions"
LEONARDO_CREATE_URL = "https://cloud.leonardo.ai/api/rest/v1/generations"
LEONARDO_GET_URL = "https://cloud.leonardo.ai/api/rest/v1/generations"  # GET {LEONARDO_GET_URL}/{generationId}

# Model ID we will use (Lightning XL example). Update from dashboard if changed.
LEONARDO_LIGHTNING_MODEL_ID = os.getenv("LEONARDO_MODEL_ID") or "ac614f96-1082-45bf-be9d-757f2d31c174" # DreamShaper v7

# Defaults for image sizes (we request 1024x768 and then resize to 1080x1350 IG)
LEONARDO_REQUEST_WIDTH = 1024
LEONARDO_REQUEST_HEIGHT = 768

# Output
OUTPUT_DIR = os.path.join(BASE_DIR, "outputs")
os.makedirs(OUTPUT_DIR, exist_ok=True)

# Polling
LEONARDO_POLL_INTERVAL = float(os.getenv("LEONARDO_POLL_INTERVAL", "2.5"))
LEONARDO_POLL_MAX_SECS = int(os.getenv("LEONARDO_POLL_MAX_SECS", "120"))

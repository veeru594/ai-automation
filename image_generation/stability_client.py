# stability_client.py
import os
import base64
import requests
import pathlib
from dotenv import load_dotenv

# ✅ Explicitly load the .env file from this same folder
env_path = pathlib.Path(__file__).parent / ".env"
print(f"Loading .env from: {env_path}")
load_dotenv(dotenv_path=env_path)

# ✅ Now read the key
STABILITY_KEY = os.getenv("STABILITY_KEY")
STABILITY_URL = os.getenv("STABILITY_URL", "https://api.stability.ai/v2beta/stable-image/generate/core")

if not STABILITY_KEY:
    raise ValueError(f"Missing STABILITY_KEY. Tried loading from {env_path}")

def generate_image(prompt, options=None):
    """Generate an image using Stability AI (multipart/form-data)."""
    if options is None:
        options = {}

    # Construct proper multipart payload
    form_data = {
        "prompt": (None, prompt),
        "mode": (None, "text-to-image"),
        "aspect_ratio": (None, options.get("aspect_ratio", "1:1")),
        "output_format": (None, "png")
    }

    headers = {
        "Authorization": f"Bearer {STABILITY_KEY}",
        "Accept": "application/json"
    }

    response = requests.post(STABILITY_URL, headers=headers, files=form_data)

    if response.status_code != 200:
        # For debugging, show the full payload details in logs
        raise ImageGenerationError(
            f"Stability AI error {response.status_code}: {response.text}"
        )

    # The API returns base64 under data.artifacts[0].base64
    data = response.json()
    try:
        b64 = data["artifacts"][0]["base64"]
    except (KeyError, IndexError) as e:
        raise ImageGenerationError(f"Malformed Stability response: {e}\nFull data: {data}")

    return {"b64": b64, "mime": "image/png", "source": "stability","raw_response":"parsed-json-from-stability-if-available"}


class ImageGenerationError(Exception):
    pass

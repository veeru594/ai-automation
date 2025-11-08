# openai_client.py
import os
import base64
from openai import OpenAI

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def generate_dalle_image(prompt, size="1024x1024"):
    """Generate an image from DALL·E 3 and return base64 data."""
    try:
        response = client.images.generate(
            model="gpt-image-1",
            prompt=prompt,
            size=size
        )
        b64 = response.data[0].b64_json
        return {"b64": b64, "mime": "image/png", "source": "dalle3"}
    except Exception as e:
        raise Exception(f"DALL·E generation failed: {str(e)}")

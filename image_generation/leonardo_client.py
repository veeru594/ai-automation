import os
import time
import requests
from typing import Optional, Dict, Any
from PIL import Image
from ai_brain.config import (
    LEONARDO_API_KEY,
    LEONARDO_CREATE_URL,
    LEONARDO_GET_URL,
    LEONARDO_LIGHTNING_MODEL_ID,  # You will replace this with Phoenix ID in .env
    LEONARDO_REQUEST_WIDTH,
    LEONARDO_REQUEST_HEIGHT,
    LEONARDO_POLL_INTERVAL,
    LEONARDO_POLL_MAX_SECS,
)

# Header for Leonardo API calls
HEADERS = {
    "Authorization": f"Bearer {LEONARDO_API_KEY}" if LEONARDO_API_KEY else "",
    "Content-Type": "application/json",
    "Accept": "application/json",
}


# ----------------------------
# Internal helpers
# ----------------------------

def _safe_post(payload: dict) -> Dict[str, Any]:
    """POST wrapper to Leonardo with error safety."""
    try:
        r = requests.post(LEONARDO_CREATE_URL, headers=HEADERS, json=payload, timeout=60)
        return {"status_code": r.status_code, "json": _safe_json(r)}
    except Exception as e:
        return {"error": f"Request failed: {e}"}


def _safe_json(response):
    """Safely parse JSON, fallback to raw text."""
    try:
        return response.json()
    except Exception:
        return {"raw_text": getattr(response, "text", "<no-text>")}


# ----------------------------
# MAIN: Create Leonardo Job
# ----------------------------

def create_generation(
    prompt: str,
    model_id: Optional[str] = None,
    width: int = None,
    height: int = None,
    num_images: int = 1,
    seed: Optional[int] = None,
    negative_prompt: Optional[str] = None
) -> Dict[str, Any]:
    """
    Create a Leonardo generation job. Returns dict with status + json.
    """
    if not LEONARDO_API_KEY:
        return {"error": "Leonardo API key not set."}

    payload = {
        "prompt": prompt,
        "width": width or LEONARDO_REQUEST_WIDTH,
        "height": height or LEONARDO_REQUEST_HEIGHT,
        "num_images": num_images,
        # "presetStyle": "DYNAMIC", # Removed for compatibility test
        # "num_inference_steps": 15
    }

    mid = model_id
    if mid is None:
        mid = LEONARDO_LIGHTNING_MODEL_ID
        
    if mid and mid != "SKIP":
        payload["modelId"] = mid

    if seed is not None:
        payload["seed"] = seed
    
    # Add negative prompt to block unwanted elements
    if negative_prompt:
        payload["negativePrompt"] = negative_prompt

    return _safe_post(payload)


# ----------------------------
# Polling until generation completes
# ----------------------------

def poll_generation(generation_id: str) -> Dict[str, Any]:
    """
    Poll until Leonardo job completes or times out.
    """
    if not LEONARDO_API_KEY:
        return {"error": "Leonardo API key not set."}

    url = f"{LEONARDO_GET_URL}/{generation_id}"
    start = time.time()

    while True:
        try:
            resp = requests.get(url, headers=HEADERS, timeout=30)
            data = _safe_json(resp)
        except Exception as e:
            return {"error": f"Poll request failed: {e}"}

        # Extract status
        status = None

        if isinstance(data, dict):
            # Common Leonardo status patterns
            if "generations_by_pk" in data:
                status = data["generations_by_pk"].get("status")
            elif "sdGenerationJob" in data:
                status = data["sdGenerationJob"].get("status")
            elif "status" in data:
                status = data.get("status")

        # If job finished
        if status and str(status).upper() in ("COMPLETE", "FINISHED", "SUCCEEDED"):
            return data

        # Some responses include images directly
        if (
            "generations_by_pk" in data
            and isinstance(data["generations_by_pk"], dict)
            and data["generations_by_pk"].get("generated_images")
        ):
            return data

        # Timeout
        if time.time() - start > LEONARDO_POLL_MAX_SECS:
            return {"error": "Poll timed out", "resp": data}

        time.sleep(LEONARDO_POLL_INTERVAL)


# ----------------------------
# Extract URL from final JSON
# ----------------------------

def extract_image_url(resp: dict) -> Optional[str]:
    """
    Find the generated image URL inside Leonardo response.
    """

    try:
        # Case 1: generations_by_pk
        if "generations_by_pk" in resp:
            imgs = resp["generations_by_pk"].get("generated_images", [])
            if imgs and "url" in imgs[0]:
                return imgs[0]["url"]

        # Case 2: direct list
        if "generated_images" in resp:
            imgs = resp["generated_images"]
            if imgs and "url" in imgs[0]:
                return imgs[0]["url"]

        return None

    except Exception:
        return None


# ----------------------------
# Download final file
# ----------------------------

def download_image(url: str, out_path: str) -> Dict[str, Any]:
    try:
        r = requests.get(url, timeout=60)
        r.raise_for_status()

        os.makedirs(os.path.dirname(out_path), exist_ok=True)

        with open(out_path, "wb") as f:
            f.write(r.content)

        return {"ok": True, "path": out_path}

    except Exception as e:
        return {"error": f"Download failed: {e}", "url": url}


# ----------------------------
# Full pipeline: create → poll → extract → download
# ----------------------------

def generate_image_with_poll(
    prompt: str,
    out_path: str,
    model_id: Optional[str] = None,
    seed: Optional[int] = None,
    negative_prompt: Optional[str] = None
) -> Dict[str, Any]:

    # 1. Create job (with negative prompt to block unwanted elements)
    create = create_generation(
        prompt, 
        model_id=model_id, 
        seed=seed, 
        num_images=1,
        negative_prompt=negative_prompt
    )

    if create.get("error"):
        return create

    j = create.get("json", {})

    # Extract generationId
    gen_id = None
    if "sdGenerationJob" in j:
        gen_id = j["sdGenerationJob"].get("generationId")
    elif "generations_by_pk" in j:
        gen_id = j["generations_by_pk"].get("id")
    elif "generationId" in j:
        gen_id = j["generationId"]

    if not gen_id:
        return {"error": "No generationId returned", "resp": j}

    # 2. Poll job status
    poll = poll_generation(gen_id)
    if poll.get("error"):
        return {"error": "Poll failed", "resp": poll}

    # 3. Extract image URL
    img_url = extract_image_url(poll)
    if not img_url:
        return {"error": "Could not extract image URL", "resp": poll}

    # 4. Download final image
    return download_image(img_url, out_path)

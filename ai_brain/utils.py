# ai_brain/utils.py
import re
import json


def strip_fences(text: str) -> str:
    if not isinstance(text, str):
        return text
    text = re.sub(r"^```(?:json)?\s*", "", text, flags=re.IGNORECASE)
    text = re.sub(r"\s*```$", "", text, flags=re.IGNORECASE)
    return text.strip()


def find_first_json_block(text: str) -> str:
    if not isinstance(text, str):
        raise ValueError("Input not a string")
    start = text.find("{")
    if start == -1:
        raise ValueError("No JSON object start found")
    depth = 0
    for i in range(start, len(text)):
        ch = text[i]
        if ch == "{":
            depth += 1
        elif ch == "}":
            depth -= 1
            if depth == 0:
                return text[start:i + 1]
    raise ValueError("Balanced JSON object not found")


def safe_load_json(text: str):
    s = strip_fences(text)
    try:
        return json.loads(s)
    except Exception:
        try:
            block = find_first_json_block(s)
            return json.loads(block)
        except Exception as e:
            raise ValueError(f"JSON parse failed: {e}")

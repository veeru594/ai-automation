import json
import os
from pathlib import Path

MEMORY_FILE = Path(__file__).parent.parent / "posted_titles.json"
MAX_MEMORY = 50


def normalize_title(title: str) -> str:
    """
    Normalize title for dedup comparison.
    Strips punctuation, lowercases, removes extra spaces.
    """
    return "".join(c.lower() for c in title if c.isalnum() or c.isspace()).strip()


def load_posted_titles():
    """
    Load previously posted titles from memory.
    Returns list of normalized titles.
    """
    if not MEMORY_FILE.exists():
        return []
    
    try:
        with open(MEMORY_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except:
        return []


def save_posted_title(title: str):
    """
    Add a new posted title to memory.
    Keeps only last MAX_MEMORY items.
    """
    normalized = normalize_title(title)
    
    posted = load_posted_titles()
    
    # Avoid duplicates in memory itself
    if normalized not in posted:
        posted.append(normalized)
    
    # Keep only recent items
    posted = posted[-MAX_MEMORY:]
    
    MEMORY_FILE.parent.mkdir(parents=True, exist_ok=True)
    
    with open(MEMORY_FILE, "w", encoding="utf-8") as f:
        json.dump(posted, f, indent=2)


def is_duplicate(title: str) -> bool:
    """
    Check if title was already posted.
    """
    normalized = normalize_title(title)
    posted = load_posted_titles()
    return normalized in posted

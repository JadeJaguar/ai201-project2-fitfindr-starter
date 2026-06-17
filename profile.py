import json
import os
from utils.data_loader import get_empty_wardrobe

PROFILE_PATH = "profile.json"


def save_profile(wardrobe: dict) -> None:
    """Save the user's wardrobe to a local profile.json file."""
    try:
        with open(PROFILE_PATH, "w", encoding="utf-8") as f:
            json.dump(wardrobe, f, indent=2)
    except Exception as e:
        print(f"Could not save profile: {e}")


def load_profile() -> dict:
    """
    Load the user's wardrobe from profile.json.
    Falls back to empty wardrobe if file is missing or corrupted.
    """
    if not os.path.exists(PROFILE_PATH):
        return get_empty_wardrobe()
    try:
        with open(PROFILE_PATH, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return get_empty_wardrobe()


def profile_exists() -> bool:
    """Returns True if a saved profile exists."""
    return os.path.exists(PROFILE_PATH)
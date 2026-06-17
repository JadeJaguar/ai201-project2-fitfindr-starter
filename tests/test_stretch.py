from agent import run_agent
from utils.data_loader import get_example_wardrobe
from profile import save_profile, load_profile, profile_exists
import os

# run pytest tests/ -v

# Retry logic tests

def test_retry_removes_size_filter():
    session = run_agent(
        query="vintage graphic tee size XXS under $200",
        wardrobe=get_example_wardrobe(),
    )
    assert session["error"] is None
    assert session["retry_note"] is not None
    assert "XXS" in session["retry_note"]

def test_no_results_after_retry_sets_error():
    session = run_agent(
        query="designer ballgown size XXS under $5",
        wardrobe=get_example_wardrobe(),
    )
    assert session["error"] is not None
    assert session["fit_card"] is None


# Style profile memory tests

def test_save_and_load_profile():
    wardrobe = get_example_wardrobe()
    save_profile(wardrobe)
    loaded = load_profile()
    assert loaded["items"] == wardrobe["items"]

def test_load_profile_missing_file():
    if os.path.exists("profile.json"):
        os.remove("profile.json")
    result = load_profile()
    assert result["items"] == []
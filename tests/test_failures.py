# to run: pytest tests/test_failures.py -v -s

from tools import search_listings, suggest_outfit, create_fit_card
from utils.data_loader import get_empty_wardrobe


def test_no_listings_returns_empty_list():
    results = search_listings("designer ballgown", size="XXS", max_price=5)
    print(f"\nTest 1 - No results: {results}")
    assert results == []


def test_empty_wardrobe_returns_general_advice():
    results = search_listings("vintage graphic tee", size=None, max_price=50)
    result = suggest_outfit(results[0], get_empty_wardrobe())
    print(f"\nTest 2 - Empty wardrobe advice:\n{result}")
    assert isinstance(result, str)
    assert len(result) > 0


def test_empty_outfit_returns_error_message():
    results = search_listings("vintage graphic tee", size=None, max_price=50)
    result = create_fit_card("", results[0])
    print(f"\nTest 3 - Empty outfit message: {result}")
    assert "missing" in result.lower()
from tools import search_listings, suggest_outfit, create_fit_card
from utils.data_loader import get_example_wardrobe, get_empty_wardrobe
from tools import compare_price

# to run: pytest tests/test_tools.py -v

# search_listings tests

def test_search_returns_results():
    results = search_listings("vintage graphic tee", size=None, max_price=50)
    assert isinstance(results, list)
    assert len(results) > 0

def test_search_empty_results():
    results = search_listings("designer ballgown", size="XXS", max_price=5)
    assert results == []

def test_search_price_filter():
    results = search_listings("jacket", size=None, max_price=10)
    assert all(item["price"] <= 10 for item in results)

def test_search_size_filter():
    results = search_listings("tee", size="XL", max_price=100)
    assert all("xl" in item["size"].lower() for item in results)


# suggest_outfit tests

def test_suggest_outfit_with_wardrobe():
    results = search_listings("vintage graphic tee", size=None, max_price=50)
    result = suggest_outfit(results[0], get_example_wardrobe())
    assert isinstance(result, str)
    assert len(result) > 0

def test_suggest_outfit_empty_wardrobe():
    results = search_listings("vintage graphic tee", size=None, max_price=50)
    result = suggest_outfit(results[0], get_empty_wardrobe())
    assert isinstance(result, str)
    assert len(result) > 0


# create_fit_card tests

def test_create_fit_card_returns_caption():
    results = search_listings("vintage graphic tee", size=None, max_price=50)
    wardrobe = get_example_wardrobe()
    outfit = suggest_outfit(results[0], wardrobe)
    result = create_fit_card(outfit, results[0])
    assert isinstance(result, str)
    assert len(result) > 0

def test_create_fit_card_empty_outfit():
    results = search_listings("vintage graphic tee", size=None, max_price=50)
    result = create_fit_card("", results[0])
    assert "missing" in result.lower()

def test_suggest_outfit_empty_wardrobe_gives_advice():
    results = search_listings("vintage graphic tee", size=None, max_price=50)
    result = suggest_outfit(results[0], get_empty_wardrobe())
    assert any(word in result.lower() for word in ["pair", "style", "wear", "outfit", "look"])

def test_create_fit_card_empty_outfit_gives_informative_message():
    results = search_listings("vintage graphic tee", size=None, max_price=50)
    result = create_fit_card("", results[0])
    assert "missing" in result.lower()
    assert len(result) > 20


# compare_price tests

def test_compare_price_returns_string():
    results = search_listings("vintage graphic tee", size=None, max_price=50)
    result = compare_price(results[0])
    assert isinstance(result, str)
    assert len(result) > 0

def test_compare_price_no_comparables():
    fake_item = {
        "id": "fake_001",
        "category": "nonexistent",
        "style_tags": ["xyz123"],
        "price": 50.0
    }
    result = compare_price(fake_item)
    assert "not enough" in result.lower()
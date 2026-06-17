"""
tools.py

The three required FitFindr tools. Each tool is a standalone function that
can be called and tested independently before being wired into the agent loop.

Complete and test each tool before moving to agent.py.

Tools:
    search_listings(description, size, max_price)  → list[dict]
    suggest_outfit(new_item, wardrobe)              → str
    create_fit_card(outfit, new_item)               → str
"""

import os

from dotenv import load_dotenv
from groq import Groq

from utils.data_loader import load_listings

load_dotenv()


# -- Groq client --------------------------------

def _get_groq_client():
    """Initialize and return a Groq client using GROQ_API_KEY from .env."""
    api_key = os.environ.get("GROQ_API_KEY")
    if not api_key:
        raise ValueError(
            "GROQ_API_KEY not set. Add it to a .env file in the project root."
        )
    return Groq(api_key=api_key)


# -- Tool 1: search_listings --------------------------------

def search_listings(
    description: str,
    size: str | None = None,
    max_price: float | None = None,
) -> list[dict]:
    """
    Search the mock listings dataset for items matching the description,
    optional size, and optional price ceiling.

    Args:
        description: Keywords describing what the user is looking for
                     (e.g., "vintage graphic tee").
        size:        Size string to filter by, or None to skip size filtering.
                     Matching is case-insensitive (e.g., "M" matches "S/M").
        max_price:   Maximum price (inclusive), or None to skip price filtering.

    Returns:
        A list of matching listing dicts, sorted by relevance (best match first).
        Returns an empty list if nothing matches — does NOT raise an exception.

    Each listing dict has the following fields:
        id, title, description, category, style_tags (list), size,
        condition, price (float), colors (list), brand, platform

    TODO:
        1. Load all listings with load_listings().
        2. Filter by max_price and size (if provided).
        3. Score each remaining listing by keyword overlap with `description`.
        4. Drop any listings with a score of 0 (no relevant matches).
        5. Sort by score, highest first, and return the listing dicts.

    Before writing code, fill in the Tool 1 section of planning.md.
    """
    listings = load_listings()

    # Filter by price
    if max_price is not None:
        listings = [l for l in listings if l["price"] <= max_price]

    # Filter by size
    if size is not None:
        listings = [l for l in listings if size.lower() in l["size"].lower()]

    # Score by keyword overlap with description
    keywords = description.lower().split()

    def score(listing):
        text = (
            listing["title"].lower() + " " +
            listing["description"].lower() + " " +
            " ".join(listing["style_tags"]).lower()
        )
        return sum(1 for word in keywords if word in text)

    scored = [(score(l), l) for l in listings]
    scored = [(s, l) for s, l in scored if s > 0]
    scored.sort(key=lambda x: x[0], reverse=True)

    return [l for _, l in scored]


# -- Tool 2: suggest_outfit --------------------------------

def suggest_outfit(new_item: dict, wardrobe: dict) -> str:
    """
    Given a thrifted item and the user's wardrobe, suggest 1–2 complete outfits.

    Args:
        new_item: A listing dict (the item the user is considering buying).
        wardrobe: A wardrobe dict with an 'items' key containing a list of
                  wardrobe item dicts. May be empty — handle this gracefully.

    Returns:
        A non-empty string with outfit suggestions.
        If the wardrobe is empty, offer general styling advice for the item
        rather than raising an exception or returning an empty string.

    TODO:
        1. Check whether wardrobe['items'] is empty.
        2. If empty: call the LLM with a prompt for general styling ideas
           (what kinds of items pair well, what vibe it suits, etc.).
        3. If not empty: format the wardrobe items into a prompt and ask
           the LLM to suggest specific outfit combinations using the new item
           and named pieces from the wardrobe.
        4. Return the LLM's response as a string.

    Before writing code, fill in the Tool 2 section of planning.md.
    """
    client = _get_groq_client()

    if not wardrobe.get("items"):
        prompt = (
            f"A user is considering buying this secondhand item:\n"
            f"Title: {new_item['title']}\n"
            f"Description: {new_item['description']}\n"
            f"Style tags: {', '.join(new_item['style_tags'])}\n"
            f"Colors: {', '.join(new_item['colors'])}\n\n"
            f"They have not shared their wardrobe. Give them 1 to 2 general outfit ideas "
            f"for this item. Keep it casual and specific to the item's vibe."
        )
    else:
        wardrobe_lines = "\n".join(
            f"- {item['name']} ({', '.join(item['style_tags'])})"
            for item in wardrobe["items"]
        )
        prompt = (
            f"A user is considering buying this secondhand item:\n"
            f"Title: {new_item['title']}\n"
            f"Description: {new_item['description']}\n"
            f"Style tags: {', '.join(new_item['style_tags'])}\n"
            f"Colors: {', '.join(new_item['colors'])}\n\n"
            f"Their current wardrobe:\n{wardrobe_lines}\n\n"
            f"Suggest 1 to 2 specific outfit combinations using the new item and named "
            f"pieces from their wardrobe. Keep it casual and practical."
        )

    try:
        response = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[{"role": "user", "content": prompt}],
            max_tokens=300,
        )
        result = response.choices[0].message.content.strip()
        return result if result else "Could not generate outfit suggestions. Please try again."
    except Exception as e:
        return f"Could not generate outfit suggestions. API error: {str(e)}"

# -- Tool 3: create_fit_card --------------------------------

def create_fit_card(outfit: str, new_item: dict) -> str:
    """
    Generate a short, shareable outfit caption for the thrifted find.

    Args:
        outfit:   The outfit suggestion string from suggest_outfit().
        new_item: The listing dict for the thrifted item.

    Returns:
        A 2–4 sentence string usable as an Instagram/TikTok caption.
        If outfit is empty or missing, return a descriptive error message
        string — do NOT raise an exception.

    The caption should:
    - Feel casual and authentic (like a real OOTD post, not a product description)
    - Mention the item name, price, and platform naturally (once each)
    - Capture the outfit vibe in specific terms
    - Sound different each time for different inputs (use higher LLM temperature)

    TODO:
        1. Guard against an empty or whitespace-only outfit string.
        2. Build a prompt that gives the LLM the item details and the outfit,
           and asks for a caption matching the style guidelines above.
        3. Call the LLM and return the response.

    Before writing code, fill in the Tool 3 section of planning.md.
    """
    if not outfit or not outfit.strip():
        return "Could not create a fit card because the outfit description is missing."

    client = _get_groq_client()

    prompt = (
        f"Write a 2 to 4 sentence Instagram caption for this thrifted outfit.\n\n"
        f"Item: {new_item['title']}\n"
        f"Price: ${new_item['price']}\n"
        f"Platform: {new_item['platform']}\n"
        f"Outfit: {outfit}\n\n"
        f"Rules:\n"
        f"- Sound casual and authentic, like a real person posting an OOTD\n"
        f"- Mention the item name, price, and platform once each, naturally\n"
        f"- Capture the vibe of the outfit in specific terms\n"
        f"- Do not sound like a product description\n"
        f"- You can use one emoji if it fits"
    )

    try:
        response = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[{"role": "user", "content": prompt}],
            max_tokens=150,
            temperature=1.2,
        )
        result = response.choices[0].message.content.strip()
        return result if result else "Could not create a fit card. Please try again."
    except Exception as e:
        return f"Could not create a fit card. API error: {str(e)}"

# -- Tool 4: compare_price --------------------------------

def compare_price(item: dict) -> str:
    """
    Estimates whether an item's price is fair based on comparable listings.

    Args:
        item: A listing dict to evaluate.

    Returns:
        A string describing whether the price is fair, cheap, or expensive
        compared to similar items in the dataset.
    """
    listings = load_listings()

    comparable = [
        l for l in listings
        if l["category"] == item["category"]
        and l["id"] != item["id"]
        and any(tag in l["style_tags"] for tag in item["style_tags"])
    ]

    if not comparable:
        return "Not enough similar listings to compare prices."

    avg_price = sum(l["price"] for l in comparable) / len(comparable)
    item_price = item["price"]
    diff = item_price - avg_price

    if diff < -5:
        verdict = "below average"
    elif diff > 5:
        verdict = "above average"
    else:
        verdict = "about average"

    return (
        f"This item is priced {verdict} for its category. "
        f"Similar items go for around ${avg_price:.2f} on average. "
        f"This one is ${item_price:.2f}."
    )
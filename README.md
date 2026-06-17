# FitFindr

FitFindr is a multi-tool AI agent that helps users find secondhand clothing and figure out how to wear it. The user types a natural language request and the agent searches listings, suggests an outfit, and generates a shareable caption.

## What's Included

```
ai201-project2-fitfindr-starter/
├── data/
│   ├── listings.json          # 40 mock secondhand listings
│   └── wardrobe_schema.json   # Wardrobe format + example wardrobe
├── utils/
│   └── data_loader.py         # Helper functions for loading the data
├── tests/
│   ├── test_tools.py          # Tool unit tests
│   └── test_failures.py       # Failure mode tests
├── tools.py                   # The three FitFindr tools
├── agent.py                   # Planning loop and session state
├── app.py                     # Gradio UI
├── planning.md                # Project spec and agent design
└── requirements.txt           # Python dependencies
```

## Setup

```bash
pip install -r requirements.txt
```

Set your Groq API key in a .env file (get a free key at https://console.groq.com):

```
GROQ_API_KEY=your_key_here
```

## How to Run
```bash
python app.py
```
Open the URL shown in your terminal.

## The Mock Listings Dataset
data/listings.json contains 40 mock secondhand listings across categories (tops, bottoms, outerwear, shoes, accessories) and styles (vintage, y2k, grunge, cottagecore, streetwear, and more).

Each listing has: id, title, description, category, style_tags, size, condition, price, colors, brand, and platform.

Load it with:
```python
from utils.data_loader import load_listings
listings = load_listings()
```

## The Wardrobe Schema

data/wardrobe_schema.json defines the format your agent uses to represent a user's existing wardrobe. It includes:

- schema: field definitions for a wardrobe item
- example_wardrobe: a sample wardrobe with 10 items you can use for testing
- empty_wardrobe: a starting template for a new user

Load an example wardrobe with:

```python
from utils.data_loader import get_example_wardrobe
wardrobe = get_example_wardrobe()
```
---
## Tool Inventory

### search_listings(description, size, max_price)
- Input: description (str), size (str or None), max_price (float or None)
- Output: A list of listing dicts sorted by relevance. Each dict has: id, title, description, category, style_tags, size, condition, price, colors, brand, platform.
- Purpose: Searches the mock listings dataset and returns items that match the user's keywords, size, and price limit.

### suggest_outfit(new_item, wardrobe)
- Input: new_item (dict), wardrobe (dict with an items key)
- Output: A string with 1 to 2 outfit suggestions.
- Purpose: Uses the Groq LLM to suggest outfit combinations using the new item and the user's existing wardrobe pieces.

### create_fit_card(outfit, new_item)
- Input: outfit (str), new_item (dict)
- Output: A 2 to 4 sentence casual caption string.
- Purpose: Generates a shareable Instagram-style caption for the outfit using the Groq LLM.

---

## Planning Loop
The agent runs these steps in order for each user query:

1. Parse the query to extract a description, size, and max price using regex.
2. Call search_listings() with the parsed values.
3. Check if results are empty. If yes, set an error message and stop. Do not call the next tools.
4. Set selected_item to the top result.
5. Call suggest_outfit() with the selected item and the user's wardrobe.
6. Call create_fit_card() with the outfit suggestion and selected item.
7. Return the session.

The key branch is after step 2. If search_listings returns nothing, the agent stops early and tells the user what to try instead. It does not call suggest_outfit with empty input.

---

## State Management
All state lives in a single session dict created at the start of each run. It holds the original query, parsed parameters, search results, selected item, wardrobe, outfit suggestion, fit card, and any error. Each tool writes its output into the session dict and the next tool reads from it. No data is re-entered by the user between steps.

---

## Error Handling
| Tool | Failure mode | What the agent does |
|------|-------------|---------------------|
| search_listings | No results match the query | Sets session["error"] to "No listings found. Try a broader description, a different size, or a higher price limit." Returns early without calling the next tools. |
| suggest_outfit | Wardrobe is empty | Calls the LLM for general styling advice about the item instead of specific combinations. Returns that as the suggestion string. |
| create_fit_card | Outfit input is empty | Returns "Could not create a fit card because the outfit description is missing." Does not raise an exception. |
| suggest_outfit | Groq API fails | Returns a clean error message string with the API error. Does not crash the UI. |
| create_fit_card | Groq API fails | Returns a clean error message string with the API error. Does not crash the UI. |

### Example from testing:
Running create_fit_card("", item) returns 
Could not create a fit card because the outfit description is missing. 

Running search_listings("designer ballgown", size="XXS", max_price=5) returns an empty list and the agent responds with a clear message telling the user to broaden their search.

---

## AI Usage

### Instance 1: search_listings implementation
I gave Claude the Tool 1 spec from planning.md including the input parameters, return value description, and failure mode. I asked it to implement the function using load_listings() from data_loader.py. Claude generated a scoring function based on keyword overlap across title, description, and style tags. I reviewed it to confirm it filtered by all three parameters and returned an empty list on no match, then tested it with 3 queries before using it.

### Instance 2: planning loop implementation
I gave Claude the Planning Loop and State Management sections from planning.md along with the Architecture diagram. I asked it to implement run_agent() in agent.py. Claude generated the full loop with regex-based query parsing and a branch on empty search results. I checked that it stored values in the session dict between steps and did not call all three tools unconditionally, then tested both the happy path and no-results path.

---

## Running Tests
Run all tool tests:
```bash
pytest tests/test_tools.py -v
```
Run all failure mode tests:
```bash
pytest tests/test_failures.py -v -s
```

---

## Stretch Features

### Retry Logic with Fallback
If search_listings returns no results and the query included a size, the agent automatically retries without the size filter and tells the user what was changed. If the retry also returns nothing, the agent stops with a clear error message.

### Price Comparison Tool: compare_price(item)
- Input: item (dict)
- Output: A string saying whether the price is below average, about average, or above average compared to similar listings in the same category.
- Added to the planning loop after the top result is selected. Shows at the bottom of the listing panel.

### Style Profile Memory
The agent saves the user's wardrobe choice to a local profile.json file after each run. On the next run, the user can select "My saved profile" to load it back without re-entering anything. If the file is missing or corrupted, the agent falls back to an empty wardrobe without crashing.

## Video Walkthrough



https://github.com/user-attachments/assets/15082726-1519-4f38-94db-cfda8c3fcd6d


<video controls src="assets/AI201_project2_walkthrough.mp4" title="Title"></video>

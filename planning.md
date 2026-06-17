# FitFindr — planning.md

> Complete this document before writing any implementation code.
> Your spec and agent diagram are what you'll use to direct AI tools (Claude, Copilot, etc.) to generate your implementation — the more specific they are, the more useful the generated code will be.
> Your planning.md will be reviewed as part of your submission.
> Update it before starting any stretch features.

---

## Tools

List every tool your agent will use. For each tool, fill in all four fields.
You must have at least 3 tools. The three required tools are listed — add any additional tools below them.

### Tool 1: search_listings

**What it does:**
Searches the mock listings dataset and returns items that match the user's description, size, and price limit. Returns an empty list if nothing matches.

**Input parameters:**
- `description` (str): Keywords describing the item the user wants (e.g. "vintage graphic tee")
- `size` (str or None): Size to filter by, case-insensitive. Pass None to skip size filtering.
- `max_price` (float or None): Maximum price inclusive. Pass None to skip price filtering.

**What it returns:**
A list of listing dicts sorted by relevance score, best match first. Each dict has: id, title, description, category, style_tags (list), size, condition, price (float), colors (list), brand, platform. Returns an empty list if no matches are found.

**What happens if it fails or returns nothing:**
The agent sets session["error"] to "No listings found for your search. Try a broader description, a different size, or a higher price limit." It returns the session early and does not call suggest_outfit.

---

### Tool 2: suggest_outfit

**What it does:**
Takes the selected listing and the user's wardrobe and asks the LLM to suggest 1 to 2 complete outfit combinations using the new item and existing wardrobe pieces.

**Input parameters:**
- `new_item` (dict): The listing dict for the item the user is considering buying.
- `wardrobe` (dict): A wardrobe dict with an 'items' key containing a list of wardrobe item dicts. Can be empty.

**What it returns:**
A non-empty string with outfit suggestions. If the wardrobe is empty, the string contains general styling advice for the item instead of specific combinations.

**What happens if it fails or returns nothing:**
If wardrobe['items'] is empty, the agent calls the LLM for general styling advice instead of crashing. If the LLM returns an empty response, the tool returns the string "Could not generate outfit suggestions. Please try again."

---

### Tool 3: create_fit_card

**What it does:**
Generates a short 2 to 4 sentence caption for the outfit, written in a casual social media style like an Instagram OOTD post.

**Input parameters:**
- `outfit` (str): The outfit suggestion string returned by suggest_outfit.
- `new_item` (dict): The listing dict for the thrifted item, used to pull in the title, price, and platform.

**What it returns:**
A 2 to 4 sentence string that mentions the item name, price, and platform naturally, captures the outfit vibe, and sounds casual and authentic. Returns an error message string if outfit is empty.

**What happens if it fails or returns nothing:**
If outfit is empty or whitespace only, the tool returns the string "Could not create a fit card because the outfit description is missing." It does not raise an exception.

---

### Additional Tools (if any)

### Tool 4: compare_price

**What it does:**
Looks at comparable listings in the dataset with the same category and similar style tags, and tells the user whether the item's price is fair, cheap, or expensive.

**Input parameters:**
- `item` (dict): The listing dict to evaluate.

**What it returns:**
A string describing whether the price is below average, above average, or about average, along with the average price of comparable items.

**What happens if it fails or returns nothing:**
If no comparable items are found in the dataset, returns "Not enough similar listings to compare prices." Does not raise an exception.

---

## Planning Loop

**How does your agent decide which tool to call next?**

The agent runs a fixed sequence but with a branch after the first step.

1. Parse the query to extract description, size, and max_price. Store in session["parsed"].
2. Call search_listings() with the parsed values. Store results in session["search_results"].
3. Check if session["search_results"] is empty. If yes, set session["error"] and return early. Do not call suggest_outfit.
4. If results exist, set session["selected_item"] to results[0].
    - 4b. Call compare_price() with session["selected_item"]. Store result in session["price_comparison"].
5. Call suggest_outfit() with session["selected_item"] and session["wardrobe"]. Store result in session["outfit_suggestion"].
6. Call create_fit_card() with session["outfit_suggestion"] and session["selected_item"]. Store result in session["fit_card"].
7. Return the session.

---

## State Management

**How does information from one tool get passed to the next?**

All state is stored in a single session dict created at the start of each run. The dict holds: query, parsed parameters, search results, selected item, wardrobe, outfit suggestion, fit card, and error. Each tool writes its output into the session dict and the next tool reads from it. No data is re-entered by the user between steps.

---

## Error Handling

For each tool, describe the specific failure mode you're handling and what the agent does in response.

| Tool | Failure mode | Agent response |
|------|-------------|----------------|
| search_listings | No results match the query | Set session["error"] to "No listings found. Try a broader description, a different size, or a higher price limit." Return early without calling the next tools. |
| suggest_outfit | Wardrobe is empty | Call the LLM for general styling advice about the item instead of specific outfit combinations. Return that as the suggestion string. |
| create_fit_card | Outfit input is empty or whitespace | Return the string "Could not create a fit card because the outfit description is missing." Do not raise an exception. |

---

## Architecture

```
User query
    │
    ▼
Planning Loop
    │
    ├─► Step 1: Parse query → session["parsed"] (description, size, max_price)
    │
    ├─► Step 2: search_listings(description, size, max_price)
    │       │
    │       ├── results=[] and size was given → retry with size=None
    │       │       │
    │       │       ├── retry results=[] → set session["error"] → return early ─► END
    │       │       │
    │       │       └── retry results found → set session["retry_note"]
    │       │
    │       ├── results=[] and no size → set session["error"] → return early ───► END
    │       │
    │       └── results=[item, ...] → session["selected_item"] = results[0]
    │
    ├─► Step 3: compare_price(selected_item)
    │       │
    │       └── session["price_comparison"] = verdict string
    │
    ├─► Step 4: suggest_outfit(selected_item, wardrobe)
    │       │
    │       ├── wardrobe empty → LLM gives general styling advice
    │       │
    │       └── wardrobe has items → LLM suggests specific combinations
    │               │
    │               └── session["outfit_suggestion"] = result
    │
    └─► Step 5: create_fit_card(outfit_suggestion, selected_item)
            │
            ├── outfit empty → return error message string
            │
            └── session["fit_card"] = caption string
                    │
                    ▼
                Return session
```

---

## AI Tool Plan

<!-- For each part of the implementation below, describe:
     - Which AI tool you plan to use (Claude, Copilot, ChatGPT, etc.)
     - What you'll give it as input (which sections of this planning.md, your agent diagram)
     - What you expect it to produce
     - How you'll verify the output matches your spec before moving on

     "I'll use AI to help me code" is not a plan.
     "I'll give Claude my Tool 1 spec (inputs, return value, failure mode) and ask it to implement
     search_listings() using load_listings() from the data loader — then test it against 3 queries
     before trusting it" is a plan. -->

**Milestone 3 - Individual tool implementations:**

For search_listings, I will give Claude the Tool 1 spec from planning.md (inputs, return value, failure mode) and ask it to implement the function using load_listings() from data_loader.py. I will check that it filters by all three parameters and handles the empty list case. Then I will test it with 3 different queries before moving on.

For suggest_outfit, I will give Claude the Tool 2 spec and ask it to implement the function using the Groq API with llama-3.3-70b-versatile. I will check that it handles the empty wardrobe case and does not crash. I will test it with both get_example_wardrobe() and get_empty_wardrobe().

For create_fit_card, I will give Claude the Tool 3 spec and ask it to implement the function using the Groq API with a higher temperature for variety. I will check that it guards against empty outfit input and run it 3 times on the same input to verify the outputs differ.

**Milestone 4 - Planning loop and state management:**

I will give Claude the Planning Loop and State Management sections plus the Architecture diagram from planning.md and ask it to implement run_agent() in agent.py. I will check that the code branches on empty search results and stores values in the session dict between steps. I will run both the happy path and the no-results path to verify the correct behavior.

---

## A Complete Interaction (Step by Step)

Write out what a full user interaction looks like from start to finish — tool call by tool call. Use a specific example query.

FitFindr takes a natural language request from the user and runs it through three tools in order. First, it searches the listings data for items that match the description, size, and price. Then it uses the found item and the user's wardrobe to suggest a full outfit. Finally, it turns that outfit into a short caption the user can share. If any tool returns nothing useful, for example no listings match the search, the agent stops early and tells the user what went wrong and what they can try instead.

**Example user query:** "I'm looking for a vintage graphic tee under $30. I mostly wear baggy jeans and chunky sneakers. What's out there and how would I style it?"

**Step 1:**
The agent parses the query and extracts description="vintage graphic tee", size=None, max_price=30.0. It calls search_listings("vintage graphic tee", size=None, max_price=30.0). The tool returns a list of matching listings sorted by relevance. The agent sets selected_item to the first result, for example "Y2K Baby Tee — Butterfly Print" at $18 on Depop.

**Step 2:**
The agent calls suggest_outfit(selected_item, wardrobe) where wardrobe is the example wardrobe with 10 items. The LLM returns a suggestion like "Pair this tee with your baggy dark wash jeans and chunky white sneakers for a 90s streetwear look. Add the black crossbody bag to finish it off."

**Step 3:**
The agent calls create_fit_card(outfit_suggestion, selected_item). The LLM returns a short caption like "thrifted this y2k butterfly tee off depop for $18 and it was made for my baggy jeans era 🦋 full look dropping soon"

**Final output to user:**
The user sees three things: the listing that was found (title, price, platform, condition), the outfit suggestion with specific pieces named, and the fit card caption ready to copy and share.


---

## Stretch Features

### Stretch 1: Retry Logic with Fallback

**What it does:**
If search_listings returns no results, the agent retries the search with the size filter removed. It then tells the user what was changed.

**How it changes the planning loop:**
After step 3 (empty results check), instead of stopping immediately, the agent checks if a size was in the parsed query. If yes, it retries search_listings with size=None and informs the user that the size filter was removed. If the retry also returns nothing, then the agent stops with an error message.

**Error handling:**
If both the original search and the retry return nothing, the agent sets session["error"] to "No listings found even after removing the size filter. Try a broader description or a higher price limit."

---

### Stretch 2: Price Comparison Tool

**What it does:**
Given a listing, it looks at comparable items in the dataset (same category, similar style tags) and tells the user if the price is fair, cheap, or expensive compared to similar items.

**Input parameters:**
- `item` (dict): The listing dict to evaluate.

**What it returns:**
A string like "This item is priced below average for its category. Similar items go for around $X."

**Error handling:**
If no comparable items are found, return "Not enough similar listings to compare prices."

---

### Stretch 3: Style Profile Memory

**What it does:**
Saves the user's wardrobe to a local JSON file so they do not have to re-enter it every session. Loads it back on the next run.

**How it works:**
Two functions: save_profile(wardrobe) writes to a local profile.json file. load_profile() reads it back. If no file exists, it falls back to get_empty_wardrobe().

**Error handling:**
If the file is missing or corrupted, fall back to get_empty_wardrobe() without crashing.
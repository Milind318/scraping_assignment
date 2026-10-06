# AI Usage

## Tool used
Claude 

## What I used it for
- Understanding the assignment requirements and the ETL pipeline structure
- Generating the initial code for the scrapers, cleaning, validation, deduplication and main.py
- Generating unit tests and a draft of the README

## Representative prompts
1. "Explain this assignment step by step and give me simple code."
2. "Give me the project as a ZIP and explain every part so I understand it."
3. "Explain this log output." / "How do I check whether scraping is done?"

## What I did myself
- Set up the environment and ran the scraper against the live websites
- Verified the output: 1,099 rows in the CSV, JSON counts matching the CSV,
  prices and ratings as numbers, and a spot-check of a known book against the website
- Studied each module so I can explain it (pagination, retries, cleaning, fingerprint deduplication)
- Tested failure handling by [describe what you actually did, e.g. using a wrong URL]

## Findings from the real run
- The real run detected 1 duplicate ("The Star-Touched Queen"), which proves the
  deduplication works on live data and not only in unit tests.
- AI-generated code needed review: [write real issues or changes you made,
  e.g. a delay value you changed, a rule you added, or a bug you found]

## How I tested
- `python -m pytest` (unit tests for cleaning, validation, deduplication, pagination)
- Full live run of `python main.py` and manual checks of the CSV, JSON and log
# Multi-Source Web Scraping & Data Consolidation

## 1. Overview
This project scrapes two practice websites, **Books to Scrape** (1,000 books) and
**Quotes to Scrape** (100 quotes), and turns them into one clean dataset.

Pipeline: `Scrape -> Clean -> Validate -> Deduplicate -> Save CSV + JSON`

## 2. Setup and Run
Python 3.10 – 3.12 (developed on 3.12).

```bash
python -m venv venv
venv\Scripts\activate             # Mac/Linux: source venv/bin/activate
pip install -r requirements.txt
python main.py                    # scrape and write output (about 1-2 minutes)
python -m pytest                  # run unit tests (no internet needed)
```

Libraries: `requests` (download pages), `beautifulsoup4` + `lxml` (read HTML),
`pytest` (tests). Everything else is the Python standard library.

## 3. Why Requests + BeautifulSoup
Both sites are plain HTML pages, so no browser tool is needed.
Selenium or Playwright would only make the program slower.

## 4. How pagination works
The scraper opens the first page, collects the records, then looks for the
"Next" button (`li.next > a`). If it exists, the scraper opens that link and repeats.
If not, it stops. Page numbers are never hard-coded, so it still works if the
site gets more or fewer pages. (Result: 50 book pages, 10 quote pages.)

## 5. Data model
Both sources use the same 10 columns:
`source, source_url, name_or_title, category, price, rating, author, tags, description, scraped_at`

| Column | Book | Quote |
|---|---|---|
| name_or_title | book title | quote text |
| price, rating | filled | empty |
| author, tags | empty | filled |
| source_url | book page | listing page of the quote |
| category, description | empty (see limitations) | empty |

Fields that don't apply stay empty. No fake values are invented.

## 6. Cleaning
Done in `processing/cleaning.py`, separate from scraping:
- remove extra spaces and non-breaking spaces
- `£51.77` -> `51.77`; rating word `Three` -> `3`
- remove curly quotes from quotes; tags lowercased, sorted, joined with `;`
- keep only full `http/https` URLs
- read pages as UTF-8 so `£` doesn't become `Â£`

## 7. Validation
Each record is checked and gets a list of problems. A record is rejected if:
the source is unknown, the name is missing, the URL is invalid, the price is
negative/non-numeric, or the rating is not 1-5. Rejections are logged and counted
by reason in the summary.

## 8. Deduplication
Each record gets a "fingerprint": lowercase, remove punctuation, collapse spaces,
then hash it (SHA-256). If a fingerprint was already seen, the record is a duplicate.
- Books: source + title
- Quotes: source + author + first 50 characters of the quote

So `"Example Book Title"`, `" Example Book Title "` and `"EXAMPLE BOOK TITLE"` count as one.
Duplicates are **removed** (first one kept) but every removal is logged and counted,
so nothing disappears silently.

On the real run, 1 duplicate was found and removed: "The Star-Touched Queen"
appears twice in Books to Scrape. Unit tests also check this logic with fake duplicates.

## 9. Error handling
- Failed requests are retried 3 times (waiting 1s, 2s, 4s); each request has a 10-second timeout
- A failed page is logged as ERROR and stops only that source; the other source still runs
- A bad record is skipped and logged without stopping the page
- Missing HTML elements become empty values instead of crashing
- 0.5-second pause between requests to be polite to the server

## 10. Output
| File | Content |
|---|---|
| `output/final_dataset.csv` | 1,099 clean, unique records |
| `output/summary_report.json` | per source: collected, rejected (with reasons), duplicates, final, plus run time |
| `logs/scraper.log` | timestamped log of the run |

Numbers add up: `collected - rejected - duplicates = final`
(1,100 collected - 0 rejected - 1 duplicate = 1,099).

## 11. Assumptions and limitations
- The sites keep their current HTML structure.
- Quotes have no page of their own, so the listing page is used as `source_url`.
- Book `category` and `description` exist only on each detail page (about 1,000 extra
  requests), so they are left empty rather than guessed.
- No resume option: an interrupted run starts again. Pages are scraped one by one.
- Duplicate rule is title-based, so two different books with the same title would be treated as one.

## 12. AI usage
See `AI_USAGE.md`.
import csv
import json
import logging
import time
from datetime import datetime, timezone
from pathlib import Path

from processing.cleaning import COLUMNS, clean_book, clean_quote
from processing.deduplication import find_duplicates
from processing.validation import validate_record
from scrapers.base_scraper import create_session
from scrapers.books_scraper import scrape_books
from scrapers.quotes_scraper import scrape_quotes

OUTPUT_DIR = Path("output")
LOG_DIR = Path("logs")

logger = logging.getLogger("main")


def setup_logging():
    LOG_DIR.mkdir(exist_ok=True)
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
        handlers=[logging.FileHandler(LOG_DIR / "scraper.log", encoding="utf-8"),
                  logging.StreamHandler()],
    )


def process_source(name, raw_records, clean_fn):
    """Clean -> validate -> deduplicate one source. Returns (final_records, stats)."""
    reasons = {}
    rejected = 0

    # 1) clean
    cleaned = []
    for raw in raw_records:
        try:
            cleaned.append(clean_fn(raw))
        except Exception as exc:
            rejected += 1
            reasons["cleaning_error"] = reasons.get("cleaning_error", 0) + 1
            logger.warning("[%s] cleaning failed: %s", name, exc)

    # 2) validate
    valid = []
    for rec in cleaned:
        problems = validate_record(rec)
        if problems:
            rejected += 1
            for p in problems:
                reasons[p] = reasons.get(p, 0) + 1
            logger.warning("[%s] rejected %r: %s", name, rec.get("name_or_title"), problems)
        else:
            valid.append(rec)

    # 3) deduplicate
    unique, dupes = find_duplicates(valid)
    for d in dupes:
        logger.info("[%s] duplicate removed: %r", name, d["name_or_title"])

    stats = {
        "collected": len(raw_records),
        "after_cleaning": len(cleaned),
        "rejected_total": rejected,
        "rejected_by_reason": reasons,
        "duplicates_removed": len(dupes),
        "final": len(unique),
    }
    return unique, stats


def write_csv(records, path):
    OUTPUT_DIR.mkdir(exist_ok=True)
    with open(path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=COLUMNS)
        writer.writeheader()
        writer.writerows(records)


def main():
    setup_logging()
    start = time.time()
    started_at = datetime.now(timezone.utc).isoformat(timespec="seconds")
    session = create_session()

    sources = [
        ("Books to Scrape", scrape_books, clean_book),
        ("Quotes to Scrape", scrape_quotes, clean_quote),
    ]

    final_records, per_source = [], {}
    for name, scrape_fn, clean_fn in sources:
        try:
            raw = scrape_fn(session)
        except Exception as exc:   
            logger.error("Source %s failed completely: %s", name, exc)
            raw = []
        records, stats = process_source(name, raw, clean_fn)
        final_records.extend(records)
        per_source[name] = stats

    write_csv(final_records, OUTPUT_DIR / "final_dataset.csv")

    summary = {
        "started_at": started_at,
        "ended_at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "duration_seconds": round(time.time() - start, 1),
        "per_source": per_source,
        "total_collected": sum(s["collected"] for s in per_source.values()),
        "total_rejected": sum(s["rejected_total"] for s in per_source.values()),
        "total_duplicates_removed": sum(s["duplicates_removed"] for s in per_source.values()),
        "final_record_count": len(final_records),
    }
    with open(OUTPUT_DIR / "summary_report.json", "w", encoding="utf-8") as f:
        json.dump(summary, f, indent=4)

    logger.info("Done. %d final records in %.1fs", len(final_records), summary["duration_seconds"])


if __name__ == "__main__":
    main()

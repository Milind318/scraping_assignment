"""Small pure functions: value in -> cleaned value out. No internet, no files."""
import re
from datetime import datetime, timezone

BOOKS = "Books to Scrape"
QUOTES = "Quotes to Scrape"


COLUMNS = ["source", "source_url", "name_or_title", "category", "price",
           "rating", "author", "tags", "description", "scraped_at"]

RATING_MAP = {"one": 1, "two": 2, "three": 3, "four": 4, "five": 5}


def clean_text(value):
    """Collapse all whitespace (incl. non-breaking spaces). Empty -> None."""
    if value is None:
        return None
    text = " ".join(value.replace("\xa0", " ").split())
    return text or None


def strip_quotes(value):
    """Remove the curly quotes around quote text."""
    if value is None:
        return None
    return clean_text(value.strip('“”"'))


def clean_price(raw):
    """'£51.77' -> 51.77"""
    if not raw:
        return None
    match = re.search(r"\d+(?:\.\d+)?", raw.replace(",", ""))
    return float(match.group()) if match else None


def clean_rating(raw):
    """'star-rating Three' -> 3"""
    for word in (raw or "").lower().split():
        if word in RATING_MAP:
            return RATING_MAP[word]
    return None


def clean_tags(tags):
    """['Love', ' books '] -> 'books;love' (lowercase, unique, sorted)."""
    cleaned = {clean_text(t).lower() for t in (tags or []) if clean_text(t)}
    return ";".join(sorted(cleaned)) or None


def normalize_url(url):
    """Keep only full http/https URLs, otherwise None."""
    url = clean_text(url)
    if url and url.startswith(("http://", "https://")):
        return url
    return None


def _now():
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


def clean_book(raw):
    """Raw book dict -> standard record."""
    return {
        "source": BOOKS,
        "source_url": normalize_url(raw.get("url")),
        "name_or_title": clean_text(raw.get("title")),
        "category": None,
        "price": clean_price(raw.get("price_raw")),
        "rating": clean_rating(raw.get("rating_raw")),
        "author": None,
        "tags": None,
        "description": None,
        "scraped_at": _now(),
    }


def clean_quote(raw):
    """Raw quote dict -> standard record."""
    return {
        "source": QUOTES,
        "source_url": normalize_url(raw.get("url")),
        "name_or_title": strip_quotes(raw.get("text")),
        "category": None,
        "price": None,
        "rating": None,
        "author": clean_text(raw.get("author")),
        "tags": clean_tags(raw.get("tags")),
        "description": None,
        "scraped_at": _now(),
    }

"""Find duplicate records using a normalized fingerprint.

Books:  source + title
Quotes: source + author + first 50 characters of the quote
Normalization: lowercase, remove punctuation, collapse spaces, SHA-256 hash.
"""
import hashlib
import re


def make_fingerprint(rec):
    if rec["source"] == "Books to Scrape":
        key = f'{rec["source"]} {rec["name_or_title"] or ""}'
    else:
        key = f'{rec["source"]} {rec.get("author") or ""} {(rec["name_or_title"] or "")[:50]}'
    key = re.sub(r"[^\w\s]", "", key.lower())   
    key = " ".join(key.split())                  
    return hashlib.sha256(key.encode("utf-8")).hexdigest()


def find_duplicates(records):
    """Return (unique_records, duplicate_records). First occurrence is kept."""
    seen, unique, dupes = set(), [], []
    for rec in records:
        fp = make_fingerprint(rec)
        if fp in seen:
            dupes.append(rec)
        else:
            unique.append(rec)
            seen.add(fp)
    return unique, dupes

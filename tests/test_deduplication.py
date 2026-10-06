from processing.deduplication import find_duplicates


def test_duplicates_ignore_case_and_spaces():
    base = {"source": "Books to Scrape", "author": None}
    records = [
        {**base, "name_or_title": "Example Book Title"},
        {**base, "name_or_title": "  Example Book Title "},
        {**base, "name_or_title": "EXAMPLE BOOK TITLE"},
    ]
    unique, dupes = find_duplicates(records)
    assert len(unique) == 1 and len(dupes) == 2


def test_different_sources_are_not_duplicates():
    a = {"source": "Books to Scrape", "author": None, "name_or_title": "Same"}
    b = {"source": "Quotes to Scrape", "author": "X", "name_or_title": "Same"}
    unique, dupes = find_duplicates([a, b])
    assert len(unique) == 2 and not dupes


def test_quotes_use_author_and_first_50_chars():
    q1 = {"source": "Quotes to Scrape", "author": "A", "name_or_title": "Hello, World!"}
    q2 = {"source": "Quotes to Scrape", "author": "a", "name_or_title": "hello world"}
    q3 = {"source": "Quotes to Scrape", "author": "B", "name_or_title": "hello world"}
    unique, dupes = find_duplicates([q1, q2, q3])
    assert len(unique) == 2 and len(dupes) == 1

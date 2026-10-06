from processing.validation import validate_record

GOOD = {"source": "Books to Scrape", "name_or_title": "X",
        "source_url": "https://a.com", "price": 10.0, "rating": 3}


def test_valid_record():
    assert validate_record(GOOD) == []


def test_invalid_record():
    bad = {**GOOD, "name_or_title": None, "price": -1, "rating": 9, "source_url": "abc"}
    assert set(validate_record(bad)) == {"missing_name", "invalid_price",
                                         "invalid_rating", "invalid_url"}


def test_unknown_source():
    assert "unknown_source" in validate_record({**GOOD, "source": "Other"})

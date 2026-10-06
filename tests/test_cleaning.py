from processing.cleaning import (clean_book, clean_price, clean_quote, clean_rating,
                                 clean_tags, clean_text, normalize_url, strip_quotes)


def test_clean_text():
    assert clean_text("  Hello \n\xa0 World ") == "Hello World"
    assert clean_text("   ") is None
    assert clean_text(None) is None


def test_clean_price():
    assert clean_price("£51.77") == 51.77
    assert clean_price("Â£1,234.50") == 1234.50
    assert clean_price("abc") is None


def test_clean_rating():
    assert clean_rating("star-rating Three") == 3
    assert clean_rating(None) is None
    assert clean_rating("star-rating") is None


def test_strip_quotes():
    assert strip_quotes("“Be yourself.”") == "Be yourself."


def test_clean_tags():
    assert clean_tags(["Love", " books ", "love"]) == "books;love"
    assert clean_tags([]) is None


def test_normalize_url():
    assert normalize_url(" https://a.com/x ") == "https://a.com/x"
    assert normalize_url("/relative") is None


def test_clean_book_and_quote():
    book = clean_book({"title": "  A  Book ", "url": "https://x.com/b",
                       "price_raw": "£10.00", "rating_raw": "star-rating Five"})
    assert book["name_or_title"] == "A Book" and book["price"] == 10.0 and book["rating"] == 5
    quote = clean_quote({"text": "“Hi”", "author": "Me", "tags": ["a"], "url": "https://x.com"})
    assert quote["name_or_title"] == "Hi" and quote["price"] is None

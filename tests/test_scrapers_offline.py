"""Test pagination + parsing with fake HTML, so no internet is needed."""
from bs4 import BeautifulSoup

from scrapers import books_scraper, quotes_scraper
from scrapers.base_scraper import scrape_all_pages

BOOK_PAGE = """
<article class="product_pod"><h3><a href="catalogue/a_1/index.html" title="Full Title A...">Full Title...</a></h3>
<p class="star-rating Three"></p><div><p class="price_color">£51.77</p></div></article>
<article class="product_pod"><h3></h3></article>
%s
"""
NEXT = '<ul><li class="next"><a href="page-2.html">next</a></li></ul>'


class FakeResponse:
    def __init__(self, text, status=200):
        self.text, self.status_code, self.encoding = text, status, None

    def raise_for_status(self):
        if self.status_code >= 400:
            import requests
            raise requests.HTTPError(f"{self.status_code}")


class FakeSession:
    def __init__(self, pages):
        self.pages, self.requested = pages, []

    def get(self, url, timeout=None):
        self.requested.append(url)
        return self.pages.get(url, FakeResponse("", 404))


def test_books_pagination_and_missing_elements():
    pages = {
        "https://books.toscrape.com/": FakeResponse(BOOK_PAGE % NEXT),
        "https://books.toscrape.com/page-2.html": FakeResponse(BOOK_PAGE % ""),
    }
    session = FakeSession(pages)
    records = scrape_all_pages(session, books_scraper.START_URL, books_scraper.parse_page, delay=0)
    assert len(session.requested) == 2           
    assert len(records) == 4                     
    assert records[0]["title"] == "Full Title A..."
    assert records[0]["price_raw"] == "£51.77"
    assert records[1]["title"] is None           


def test_failed_page_does_not_crash():
    session = FakeSession({"https://quotes.toscrape.com/": FakeResponse("", 500)})
    records = scrape_all_pages(session, quotes_scraper.START_URL, quotes_scraper.parse_page, delay=0)
    assert records == []


def test_quotes_parse():
    html = '''<div class="quote"><span class="text">“Hi”</span><small class="author">Me</small>
    <a class="tag">x</a><a class="tag">y</a></div>'''
    recs = quotes_scraper.parse_page(BeautifulSoup(html, "lxml"), "https://quotes.toscrape.com/")
    assert recs[0]["author"] == "Me" and recs[0]["tags"] == ["x", "y"]

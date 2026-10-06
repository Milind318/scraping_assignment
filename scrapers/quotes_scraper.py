"""Everything specific to Quotes to Scrape lives here."""
import logging

from scrapers.base_scraper import scrape_all_pages

logger = logging.getLogger(__name__)

START_URL = "https://quotes.toscrape.com/"


def parse_page(soup, page_url):
    """Turn one listing page into a list of raw quote dictionaries."""
    records = []
    for quote in soup.select("div.quote"):
        try:
            text = quote.select_one("span.text")
            author = quote.select_one("small.author")
            records.append({
                "text": text.get_text() if text else None,
                "author": author.get_text() if author else None,
                "tags": [t.get_text() for t in quote.select("a.tag")],
                "url": page_url,   
            })
        except Exception as exc:
            logger.warning("Skipped a quote on %s: %s", page_url, exc)
    return records


def scrape_quotes(session):
    return scrape_all_pages(session, START_URL, parse_page)

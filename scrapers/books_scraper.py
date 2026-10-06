"""Everything specific to Books to Scrape lives here."""
import logging
from urllib.parse import urljoin

from scrapers.base_scraper import scrape_all_pages

logger = logging.getLogger(__name__)

START_URL = "https://books.toscrape.com/"


def parse_page(soup, page_url):
    """Turn one listing page into a list of raw book dictionaries."""
    records = []
    for article in soup.select("article.product_pod"):
        try:
            link = article.select_one("h3 > a")
            price = article.select_one("p.price_color")
            rating = article.select_one("p.star-rating")
            records.append({
                
                "title": link.get("title") if link else None,
                "url": urljoin(page_url, link["href"]) if link and link.get("href") else None,
                "price_raw": price.get_text() if price else None,
                # class list looks like ['star-rating', 'Three']
                "rating_raw": " ".join(rating.get("class", [])) if rating else None,
            })
        except Exception as exc: 
            logger.warning("Skipped a book on %s: %s", page_url, exc)
    return records


def scrape_books(session):
    return scrape_all_pages(session, START_URL, parse_page)

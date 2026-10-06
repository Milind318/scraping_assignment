"""Shared networking code used by both scrapers.

Two jobs:
1. create_session(): a requests Session that retries temporary errors.
2. scrape_all_pages(): download a page, parse it, follow the "next" link, repeat.
"""
import logging
import time
from urllib.parse import urljoin

import requests
from bs4 import BeautifulSoup
from requests.adapters import HTTPAdapter
from urllib3.util import Retry

logger = logging.getLogger(__name__)

DELAY_SECONDS = 0.5     
TIMEOUT_SECONDS = 10    


def create_session() -> requests.Session:
    """Session with a User-Agent and automatic retries (waits 1s, 2s, 4s)."""
    session = requests.Session()
    session.headers.update({"User-Agent": "ScrapingAssignment/1.0 (learning project)"})
    retries = Retry(total=3, backoff_factor=1.0,
                    status_forcelist=[429, 500, 502, 503, 504])
    adapter = HTTPAdapter(max_retries=retries)
    session.mount("http://", adapter)
    session.mount("https://", adapter)
    return session


def scrape_all_pages(session, start_url, parse_page, delay=DELAY_SECONDS):
    """Follow the 'next' link until there is none.

    parse_page(soup, page_url) is the source-specific function that turns
    one page into a list of raw dictionaries.
    """
    url, page_number, records = start_url, 1, []

    while url:
        logger.info("Page %d: %s", page_number, url)
        try:
            response = session.get(url, timeout=TIMEOUT_SECONDS)
            response.raise_for_status()      
            response.encoding = "utf-8"     
        except requests.RequestException as exc:
            logger.error("Failed to fetch %s: %s", url, exc)
            break                            

        soup = BeautifulSoup(response.text, "lxml")
        records.extend(parse_page(soup, url))

        next_link = soup.select_one("li.next > a")
        url = urljoin(url, next_link["href"]) if next_link else None
        page_number += 1
        time.sleep(delay)

    logger.info("Finished: %d raw records from %d pages", len(records), page_number - 1)
    return records

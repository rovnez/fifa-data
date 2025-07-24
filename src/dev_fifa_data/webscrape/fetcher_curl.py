# fetcher_curl.py
import logging
import random
import time
from curl_cffi import requests as cf_requests
from config import HEADERS, MAX_RETRIES, BACKOFF_BASE, BACKOFF_CAP, URL_DELAY_MEAN, URL_DELAY_JITTER
from rate_limiter import TokenBucket, polite_sleep
from cache import get_cached, set_cached

logger = logging.getLogger(__name__)

bucket = TokenBucket(rate_per_sec=1 / URL_DELAY_MEAN, capacity=1)


def get_page_content(url: str, use_cache=True) -> str:
    if use_cache:
        cached = get_cached(url)
        if cached:
            return cached

    bucket.acquire()  # rate-limit slot
    polite_sleep(URL_DELAY_MEAN, URL_DELAY_JITTER)

    backoff = BACKOFF_BASE
    for attempt in range(1, MAX_RETRIES + 1):
        try:
            resp = cf_requests.get(
                url,
                headers=HEADERS,
                impersonate="chrome124",
                timeout=30,
            )
            code = resp.status_code
            if code == 200 and _looks_like_html(resp.text):
                html = resp.text
                set_cached(url, html)
                return html

            logger.warning("Attempt %d: status=%s for %s", attempt, code, url)

            if code in (403, 429, 500, 502, 503):
                # do exponential backoff with jitter
                sleep_for = min(BACKOFF_CAP, backoff * random.uniform(1.0, 2.0))
                time.sleep(sleep_for)
                backoff *= 2
                continue
        except Exception as e:
            logger.exception("Attempt %d: exception for %s: %s", attempt, url, e)

        time.sleep(min(BACKOFF_CAP, backoff * random.uniform(1.0, 2.0)))
        backoff *= 2

    raise RuntimeError(f"Failed to fetch {url} after {MAX_RETRIES} attempts")


def _looks_like_html(text: str) -> bool:
    # quick sanity check: CF sometimes returns JS challenge pages
    return "<html" in text.lower() and "</html>" in text.lower()

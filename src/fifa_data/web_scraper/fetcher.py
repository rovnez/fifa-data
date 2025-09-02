from abc import ABC, abstractmethod
# import requests
from curl_cffi import requests
from curl_cffi.requests.exceptions import RequestException, HTTPError
from fifa_data.web_scraper.utils import wait_with_progress_bar

from fifa_data.web_scraper.errors import PageNotFoundError, TooManyRequestsError

import random

# Tunables
MAX_RETRIES = 6  # per-URL
BASE_DELAY = 1.0  # seconds
MAX_DELAY = 60.0  # cap in seconds
JITTER_FRAC = 0.25  # +/-25% jitter


class Fetcher(ABC):

    @abstractmethod
    def get_page_content(self, url: str): ...


class FakeFetcher(Fetcher):

    def get_page_content(self, url):
        raise NotImplementedError


def _delay_with_jitter(seconds: float) -> float:
    # full jitter around the target delay
    jitter = seconds * JITTER_FRAC
    return max(0.0, seconds + random.uniform(-jitter, jitter))


def _compute_backoff(attempt: int) -> float:
    # attempt starts at 1; exponential backoff: base * 2^(attempt-1)
    return min(MAX_DELAY, BASE_DELAY * (2 ** (attempt - 1)))




class CurlFetcher(Fetcher):

    def _get_page_content(self, url: str):
        try:
            response = requests.get(url, impersonate='chrome')
            response.raise_for_status()
            return response.text
        # Note: HTTPError is a subclass of RequestException
        except HTTPError as e:
            if e.response.status_code == 404:
                raise PageNotFoundError(f"404 Not Found: {url}") from e
            elif e.response.status_code == 429:
                raise TooManyRequestsError(f"429 Too Many Requests") from e
            raise
        except RequestException as e:
            raise ConnectionError(f"Request failed for {url}: {e}") from e

    def get_page_content(self, url: str):
        attempt = 0
        last_exception: Exception | None = None
        while attempt < MAX_RETRIES:
            attempt += 1

            try:
                text = self._get_page_content(url)
                break
            except TooManyRequestsError as e:
                retry_after = None

                if hasattr(e, "retry_after") and e.retry_after is not None:
                    retry_after = float(e.retry_after)
                elif hasattr(e, "headers") and e.headers:
                    ra = e.headers.get("Retry-After")
                    if ra is not None:
                        try:
                            retry_after = float(ra)
                        except Exception:
                            retry_after = None
        return text



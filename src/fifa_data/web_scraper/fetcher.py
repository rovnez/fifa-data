from abc import ABC, abstractmethod
# import requests
from curl_cffi import requests
from curl_cffi.requests.exceptions import RequestException, HTTPError

from fifa_data.web_scraper.errors import PageNotFoundError, TooManyRequestsError


class Fetcher(ABC):

    @abstractmethod
    def get_page_content(self, url: str): ...


class FakeFetcher(Fetcher):

    def get_page_content(self, url):
        raise NotImplementedError


class CurlFetcher(Fetcher):

    def get_page_content(self, url: str):
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

from abc import ABC, abstractmethod
import requests
import curl_cffi


class Fetcher(ABC):

    @abstractmethod
    def get_page_content(self, url: str): ...


class FakeFetcher(Fetcher):

    def get_page_content(self, url):
        raise NotImplementedError


class CurlFetcher(Fetcher):

    def get_page_content(self, url: str):
        r = curl_cffi.get(url, impersonate='chrome')
        return r.text


class RequestFetcher(Fetcher):
    HEADERS = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/138.0.0.0 Safari/537.36",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7",
        "Accept-Language": "en-US,en;q=0.5",
        "Cookie": "setting=1; hl=en-US; playerCol=ae%2Coa%2Cpt%2Cvl%2Cwg%2Ctt"
    }

    def get_page_content(self, url: str):
        session = requests.Session()

        req = session.get(url, headers=self.HEADERS)

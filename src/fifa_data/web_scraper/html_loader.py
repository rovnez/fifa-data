from abc import ABC, abstractmethod
from fifa_data.web_scraper.utils import load_html_from_dir


class HtmlLoader(ABC):

    @abstractmethod
    def get_page_content(self, url: str) -> str: ...


class FakeHtmlLoader(HtmlLoader):
    FAKE_URLS = {
        'players_25_20250717.html',
    }

    def get_page_content(self, url):
        if url not in self.FAKE_URLS:
            raise ValueError(f"Invalid URL: {url}. Expected one of: {self.FAKE_URLS}")
        html_str = load_html_from_dir(url)
        return html_str


class OnlineHtmlLoader(HtmlLoader):

    def get_page_content(self, url):
        raise NotImplementedError


BASE_URL = "https://sofifa.com"
PLAYER_LIST_URL = BASE_URL + "/players?col=oa&sort=desc&offset="

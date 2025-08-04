import datetime

from fifa_data.web_scraper.fetcher import CurlFetcher
from fifa_data.web_scraper.parser import parse_html_urls
from fifa_data.web_scraper.repository import SqliteRepository

from fifa_data.web_scraper.parse_player import PlayerParser

from fifa_data.config import DB_PATH_SCRAPER

import bs4

URL_BASE = "https://sofifa.com"
URL_EXT_PLAYER_LIST = "/players?col=vl&sort=desc&offset="
LIMIT_URLS = 3
LIMIT_PLAYERS = 10


def scrape_urls(limit: int = LIMIT_URLS, session: str = None):
    start = 0
    if not session:
        session = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f')[:-3]
    for i in range(limit):
        url = URL_BASE + URL_EXT_PLAYER_LIST + str(start)
        fetcher = CurlFetcher()
        html_str = fetcher.get_page_content(url)
        urls = parse_html_urls(html_str)
        data_writer = SqliteRepository(db_path=DB_PATH_SCRAPER, session=session)
        written_lines = data_writer.write_urls(urls)
        i += 1
        start += written_lines


# scrape_urls(session='FIRST_RUN')


def scrape_players(limit: int = LIMIT_PLAYERS, session: str = None, save_full_html: bool = False):
    if not session:
        session = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f')[:-3]
    repo = SqliteRepository(db_path=DB_PATH_SCRAPER, session=session)
    urls = repo.get_urls_in_core()
    for i, url in enumerate(urls):
        if i >= limit:
            return
        url = URL_BASE + url
        fetcher = CurlFetcher()
        player_html = fetcher.get_page_content(url)
        if save_full_html:
            repo.write_player_html(url, player_html)


def parse_players(session: str = None):
    if not session:
        session = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f')[:-3]
    repo = SqliteRepository(db_path=DB_PATH_SCRAPER, session=session)
    urls = repo.get_urls_in_core()
    for url in urls:
        url = URL_BASE + url
        html = repo.get_player_html_from_url(url)
        soup = bs4.BeautifulSoup(html)
        player_parser = PlayerParser(soup)
        player_parser.parse()


parse_players(session='TEST2')

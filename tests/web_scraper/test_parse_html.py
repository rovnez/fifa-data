from fifa_data.web_scraper.utils import load_html_from_dir
from fifa_data.web_scraper.parse_player import PlayerParser
from fifa_data.web_scraper.html_loader import FakeHtmlLoader
from fifa_data.web_scraper.parser import parse_html_urls

from fifa_data.config import DB_PATH_SCRAPER

from fifa_data.web_scraper.repository import SqliteRepository

from bs4 import BeautifulSoup

import datetime
from fifa_data.web_scraper.fetcher import CurlFetcher


def test_e2e_player_urls():
    URL = "https://sofifa.com/players?col=vl&sort=desc&offset=0"
    fetcher = CurlFetcher()
    html_str = fetcher.get_page_content(URL)
    urls = parse_html_urls(html_str)
    session = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f')[:-3]

    data_writer = SqliteRepository(db_path=DB_PATH_SCRAPER, session=session)
    data_writer.write_urls(urls)

    urls = data_writer.get_urls_from_session_in_import()
    url = urls[0]
    base = 'https://sofifa.com/'
    html_str = fetcher.get_page_content(base + url)

    bs = BeautifulSoup(html_str, 'html.parser')
    player_parser = PlayerParser(bs)
    player_parser.parse()


def test_write_urls_sqlite():
    urls = [
        '/player/123/steve/010099/',
        '/player/456/barry/500050/',
        '/player/789/georg/990001/',
    ]
    session = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f')[:-3]
    data_writer = SqliteRepository(db_path=DB_PATH_SCRAPER, session=session)
    data_writer.write_urls(urls)
    urls_from_sqlite = data_writer.get_urls_from_session_in_import()
    assert set(urls) == set(urls_from_sqlite)


def test_parse_player_urls():
    page_loader = FakeHtmlLoader()
    html_str = page_loader.get_page_content('players_25_20250717.html')
    urls = parse_html_urls(html_str)
    session = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f')[:-3]

    data_writer = SqliteRepository(db_path=DB_PATH_SCRAPER, session=session)
    data_writer.write_urls(urls)


def load_html_for_test():
    bs = load_html_from_dir('player_204366_240050.html')
    return bs


def test_parse_player():
    html_file = load_html_for_test()
    bs = BeautifulSoup(html_file, 'html.parser')
    player_parser = PlayerParser(bs)
    player_parser.parse()



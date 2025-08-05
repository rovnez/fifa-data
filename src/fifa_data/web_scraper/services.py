import time

from fifa_data.web_scraper.fetcher import CurlFetcher
from fifa_data.web_scraper.parser import parse_html_urls
from fifa_data.web_scraper.repository import SqliteRepository
from fifa_data.web_scraper.parse_player import PlayerParser
from fifa_data.web_scraper.utils import create_batch_name, wait_with_progress_bar
from fifa_data.web_scraper.errors import PageNotFoundError, TooManyRequestsError

from fifa_data.config import DB_PATH_SCRAPER, LOG_FILE_SCRAPER

import bs4

import logging

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s.%(msecs)03d (%(name)s) [%(levelname)s]: %(message)s',  # show milliseconds
    datefmt='%Y-%m-%d %H:%M:%S',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler(LOG_FILE_SCRAPER, mode="a")
    ]
)

URL_BASE = "https://sofifa.com"
URL_EXT_PLAYER_LIST = "/players?col=tt&sort=desc&offset="
# URL_EXT_PLAYER_LIST = "/players?type=all&lg%5B0%5D=10&oal=70&offset="
LIMIT_URLS = 500
LIMIT_PLAYERS = 1000




# main function to get the urls
def workflow_urls():
    # scrape urls and write to import table
    # write urls from import to core
    batch_name = create_batch_name(batch_name='initial full run')
    scrape_urls(batch_name=batch_name)
    repo = SqliteRepository(db_path=DB_PATH_SCRAPER, batch_name=batch_name)
    repo.transfer_urls_from_import_to_core()


# main function to get the player info based on the urls
def workflow_players():
    raise NotImplementedError


def scrape_urls(limit: int = LIMIT_URLS, batch_name: str = None):
    total_batch_size = 0
    if not batch_name:
        batch_name = create_batch_name()
    for i in range(limit):
        print(f"Running iteration {i + 1}...")
        url = URL_BASE + URL_EXT_PLAYER_LIST + str(total_batch_size)
        fetcher = CurlFetcher()

        try:
            html_str = fetcher.get_page_content(url)
        except PageNotFoundError:  # this is a feature - there are no more players
            logging.info(f"404 reached at offset {total_batch_size}; stopping.")
            break
        except Exception as e:
            logging.error(f"Failed to fetch {url}: {e}")
            continue
        try:
            urls = parse_html_urls(html_str)
            data_writer = SqliteRepository(db_path=DB_PATH_SCRAPER, batch_name=batch_name)
            batch_size = data_writer.write_urls(urls, idx_offset=total_batch_size)
            total_batch_size += batch_size
        except Exception as e:
            logging.error(f"Processing failed at offset {total_batch_size}: {e}")
            continue

    return total_batch_size


def scrape_players(limit: int = LIMIT_PLAYERS, batch_name: str = None, save_full_html: bool = False):
    if not batch_name:
        batch_name = create_batch_name()
    repo = SqliteRepository(db_path=DB_PATH_SCRAPER, batch_name=batch_name)
    urls = repo.get_urls_in_core()
    for i, url in enumerate(urls):
        print(f"Scraping #{i + 1} {url}")
        if i >= limit:
            return
        full_url = URL_BASE + url
        fetcher = CurlFetcher()
        try:
            player_html = fetcher.get_page_content(full_url)
        except TooManyRequestsError:
            logging.info(f"429 Too Many Requests after {i} requests")
            print("Too many requests, sleeping for 60 seconds...")
            wait_with_progress_bar(60)
            continue
        except Exception as e:
            logging.error(f"Failed to fetch {url}: {e}")
            break
        try:
            if save_full_html:
                repo.write_player_html(url, player_html)
            repo.update_player_url_status(url)
        except Exception as e:
            logging.error(f"Processing finishing html for player {url}: {e}")
            break


def parse_players(batch_name: str = None):
    if not batch_name:
        batch_name = create_batch_name()
    repo = SqliteRepository(db_path=DB_PATH_SCRAPER, batch_name=batch_name)
    urls = repo.get_urls_in_core()
    for url in urls:
        url = URL_BASE + url
        html = repo.get_player_html_from_url(url)
        soup = bs4.BeautifulSoup(html)
        player_parser = PlayerParser(soup)
        player_parser.parse()


# parse_players(batch_name='TEST2')
# workflow_urls()
scrape_players(save_full_html=True)

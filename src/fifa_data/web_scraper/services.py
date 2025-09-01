from fifa_data.web_scraper.fetcher import CurlFetcher
from fifa_data.web_scraper.parser import parse_html_urls
from fifa_data.web_scraper.repository import Repository, SqliteRepository
from fifa_data.web_scraper.parse_player import BeautifulSoupPlayerParser
from fifa_data.web_scraper.utils import create_batch_name, wait_with_progress_bar
from fifa_data.web_scraper.errors import PageNotFoundError, TooManyRequestsError
from fifa_data.web_scraper.constants import FIFA_DATA_COLUMNS

from fifa_data.config import DB_PATH_SCRAPER, LOG_FILE_SCRAPER, SCHEMA_PATH

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
URL_EXT_PLAYER_LIST = "/players?col=tt&sort=desc"
URL_EXT_PLAYER_LIST_OFFSET = "&offset="
# URL_EXT_PLAYER_LIST = "/players?type=all&lg%5B0%5D=10&oal=70&offset="
LIMIT_URLS = 50
LIMIT_PLAYERS = 25


def scrape_urls(data_writer: SqliteRepository, base_url: str = None, limit: int = LIMIT_URLS):
    total_batch_size = 0

    for i in range(limit):
        logging.info(f"Running iteration {i + 1}... (batch: {data_writer.batch_name})")

        if not base_url:
            url = URL_BASE + URL_EXT_PLAYER_LIST + URL_EXT_PLAYER_LIST_OFFSET + str(total_batch_size)
        else:
            url = base_url + URL_EXT_PLAYER_LIST_OFFSET + str(total_batch_size)

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
            batch_size = data_writer.write_urls(urls, idx_offset=total_batch_size)
            total_batch_size += batch_size
        except Exception as e:
            logging.error(f"Processing failed at offset {total_batch_size}: {e}")
            continue

    return total_batch_size


def scrape_players(repo: SqliteRepository, limit: int = LIMIT_PLAYERS):
    urls = repo.get_urls_in_core(status=0)
    for i, url in enumerate(urls):

        if i >= limit:
            return
        logging.info(f"Scraping #{i + 1} {url} (batch: {repo.batch_name})")

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
            repo.write_player_html(url, player_html)
        except Exception as e:
            logging.error(f"Processing finishing html for player {url}: {e}")
            break


def parse_players(repo: SqliteRepository, batch_name: str = None):
    urls = repo.get_urls_in_core(status=1)
    for idx, url in enumerate(urls):
        print(f"{idx+1}: {url}")
        html = repo.get_player_html_from_url(url)
        player_parser = BeautifulSoupPlayerParser(url, html)
        player_parser.parse()
        player_data = player_parser.export_player_data()
        repo.add_processed_player(player_data, url)


def validate_player_data(player_data: dict) -> bool:
    # Check type
    if not isinstance(player_data, dict):
        return False

    print(set(FIFA_DATA_COLUMNS).difference(set(player_data.keys())))

    # Check number of keys
    if len(player_data) != 107:
        return False

    return True


def workflow_urls(base_url: str = None):
    batch_name = create_batch_name()
    repo = SqliteRepository(db_path=DB_PATH_SCRAPER, batch_name=batch_name)

    scrape_urls(data_writer=repo, base_url=base_url)

    try:
        inserted = repo.transfer_urls_from_import_to_core()
    except Exception as e:
        logging.error(f"Failed to transfer URLs for batch '{batch_name}': {e}")
        return
    else:
        logging.info(f"Successfully inserted {inserted} new URLs for batch '{batch_name}'.")
        repo.clear_import_table()


def workflow_players_fetching():
    batch_name = create_batch_name()
    repo = SqliteRepository(db_path=DB_PATH_SCRAPER, batch_name=batch_name)
    scrape_players(repo)


def workflow_players_parsing():
    batch_name = create_batch_name()
    repo = SqliteRepository(db_path=DB_PATH_SCRAPER, batch_name=batch_name)
    parse_players(repo)


workflow_urls(base_url='https://sofifa.com/players?type=all&lg%5B0%5D=10&oal=76')
workflow_players_fetching()
workflow_players_parsing()

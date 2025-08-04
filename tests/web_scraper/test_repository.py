from fifa_data.config import DB_PATH_SCRAPER

from fifa_data.web_scraper.repository import SqliteRepository

import datetime

FAKE_URLS = [
    '/player/123/steve/010099/',
    '/player/456/barry/500050/',
    '/player/789/georg/990001/',
]


def test_write_urls_sqlite():
    session = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f')[:-3]
    data_writer = SqliteRepository(db_path=DB_PATH_SCRAPER, session=session)
    data_writer.write_urls(FAKE_URLS)
    urls_from_sqlite = data_writer.get_urls_from_session_in_import()
    assert set(FAKE_URLS) == set(urls_from_sqlite)


def test_write_urls_to_core_through_import():
    """We write the FAKE_URLS and check whether they indeed are present in the core table

    Returns:

    """
    session = 'TEST' + datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f')[:-3]
    data_writer = SqliteRepository(db_path=DB_PATH_SCRAPER, session=session)
    data_writer.write_urls(FAKE_URLS)
    data_writer.transfer_urls_from_import_to_core()
    urls = data_writer.get_urls_in_core()
    assert set(FAKE_URLS) <= set(urls)


def test_get_player_html_from_repository():
    player_url = "https://sofifa.com/player/188545/robert-lewandowski/250044/"
    session = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f')[:-3]
    repo = SqliteRepository(db_path=DB_PATH_SCRAPER, session=session)
    html = repo.get_player_html_from_url(player_url)
    assert len

test_get_player_html_from_repository()
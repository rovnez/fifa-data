from pathlib import Path

HTML_FILES_DIR = "C:\\Users\\bokla\\020_Areas\\data\\fifa-data\\src\\fifa_data\\cache\\html_dir"

# DB_PATH_SCRAPER = "C:\\Users\\bokla\\020_Areas\\data\\fifa-data\\data_store\\scraper.db"
# DB_PATH_SCRAPER = "C:\\Users\\bokla\\020_Areas\\data\\fifa-data\\data_store\\scraper_TEST.db"

LOG_FOLDER = Path("C:\\Users\\bokla\\020_Areas\\data\\fifa-data\\src\\fifa_data\\logs")
LOG_FILE_SCRAPER = LOG_FOLDER / 'scraper.log'

SCHEMA_PATH = Path("C:\\Users\\bokla\\020_Areas\\data\\fifa-data\\src\\fifa_data\\sql\\schema.sql")

# %% CONSTANTS

DB_PATH_SCRAPER = "C:\\Users\\bokla\\020_Areas\\data\\fifa-data\\data_store\\scraper_TEST2.db"
SCRAPER_BASE_URL = "https://sofifa.com/players?type=all&lg%5B0%5D=10&oal=70"
# FULL: URL_EXT_PLAYER_LIST = "/players?col=tt&sort=desc"


# Ensure the folder exists
LOG_FOLDER.mkdir(parents=True, exist_ok=True)

# Ensure the file exists
if not LOG_FILE_SCRAPER.exists():
    LOG_FILE_SCRAPER.touch()
from pathlib import Path

HTML_FILES_DIR = "C:\\Users\\bokla\\020_Areas\\data\\fifa-data\\src\\fifa_data\\cache\\html_dir"
SCHEMA_PATH = Path("C:\\Users\\bokla\\020_Areas\\data\\fifa-data\\src\\fifa_data\\sql\\schema.sql")

DB_PATH_SCRAPER = Path("C:\\Users\\bokla\\020_Areas\\data\\fifa-data\\data_store\\scraper.db")
DB_PATH_SCRAPER.parent.mkdir(parents=True, exist_ok=True)

LOG_FOLDER = Path("C:\\Users\\bokla\\020_Areas\\data\\fifa-data\\src\\fifa_data\\logs")
LOG_FILE_SCRAPER = LOG_FOLDER / 'scraper.log'
LOG_FOLDER.mkdir(parents=True, exist_ok=True)
if not LOG_FILE_SCRAPER.exists():
    LOG_FILE_SCRAPER.touch()

from pathlib import Path

WEBSCRAPE_BASE_DIR = "C:\\Users\\bokla\\020_Areas\\data\\fifa-data\\src\\dev_fifa_data\\webscrape"

BASE_DIR = Path(WEBSCRAPE_BASE_DIR)

HTML_SAMPLES_DIR = BASE_DIR / 'html_samples'

CACHE_DIR = BASE_DIR / '.cache'
CACHE_TTL_HOURS = 24

URL_DELAY_MEAN = 0.30  # seconds
URL_DELAY_JITTER = 0.15  # +/- jitter
MAX_RETRIES = 5
BACKOFF_BASE = 1.0  # seconds
BACKOFF_CAP = 16.0  # seconds

CONCURRENCY = 2  # parallel fetchers; keep low for CF friendliness

HEADERS = {
    "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8",
    "accept-language": "en-US,en;q=0.9",
}

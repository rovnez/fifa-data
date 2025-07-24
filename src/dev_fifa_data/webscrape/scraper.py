# scraper.py
import time
from curl_cffi import requests as cf_requests

HEADERS = {
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
                  "(KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36",
    "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8",
    "accept-language": "en-US,en;q=0.9",
}


def get_page_content(url, delay=0.3, max_retries=5):
    for attempt in range(max_retries):
        try:
            r = cf_requests.get(url, headers=HEADERS, impersonate="chrome124", timeout=30)
            if r.status_code == 200:
                time.sleep(delay)
                return r.text
            print(f"[{attempt + 1}] Status {r.status_code}, retrying...")
        except Exception as e:
            print(f"[{attempt + 1}] Error {e}, retrying...")
        time.sleep(1)
    raise RuntimeError(f"Failed after {max_retries} attempts")

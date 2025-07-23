# cache.py
import hashlib
import time
from pathlib import Path
from config import CACHE_DIR, CACHE_TTL_HOURS

CACHE_DIR.mkdir(exist_ok=True)


def _path_for(url: str) -> Path:
    h = hashlib.sha1(url.encode("utf-8")).hexdigest()
    return CACHE_DIR / f"{h}.html"


def get_cached(url: str):
    p = _path_for(url)
    if not p.exists():
        return None
    age_hours = (time.time() - p.stat().st_mtime) / 3600
    if age_hours > CACHE_TTL_HOURS:
        return None
    return p.read_text(encoding="utf-8", errors="ignore")


def set_cached(url: str, html: str):
    p = _path_for(url)
    p.write_text(html, encoding="utf-8")

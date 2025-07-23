# downloader.py
import csv
import logging
from pathlib import Path
from player_parser import parse_player
# from player_parser import parse_basic_profile as parse_player  # full row (SHOULD BE: parse_player)
from config import BASE_DIR
from utils import atomic_append
from tqdm import tqdm

logger = logging.getLogger(__name__)


def download_players(url_file: Path, out_csv: Path, header: list[str], checkpoint_file: Path):
    processed = _load_processed(checkpoint_file)
    urls = [u.strip() for u in url_file.read_text().splitlines() if u.strip()]
    to_do = [u for u in urls if u not in processed]

    if not out_csv.exists():
        atomic_append(out_csv, header)

    for url in tqdm(to_do, total=len(to_do), desc="Players"):
        try:
            row = parse_player(url)  # returns list in correct order
            atomic_append(out_csv, row)
            processed.add(url)
            _save_processed(checkpoint_file, processed)
        except Exception as e:
            logger.exception("Failed parsing %s: %s", url, e)


def _load_processed(path: Path) -> set[str]:
    if not path.exists():
        return set()
    return set(path.read_text().splitlines())


def _save_processed(path: Path, s: set[str]):
    path.write_text("\n".join(sorted(s)))

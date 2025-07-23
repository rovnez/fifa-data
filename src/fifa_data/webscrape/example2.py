import logging
from downloader import download_players
from constants import ROW_HEADER  # same header as JS
from config import BASE_DIR
import os

FILES_DIR = BASE_DIR /"files"
OUTPUT_DIR = BASE_DIR / "output"
CHECKPOINT_DIR = BASE_DIR / ".checkpoints"
CHECKPOINT_DIR.mkdir(exist_ok=True)

logging.basicConfig(level=logging.INFO,format="%(asctime)s %(levelname)s %(name)s: %(message)s")

# test or full
scan_type = 'test'

# download data
url_file = FILES_DIR / f"player-urls-{scan_type}.csv"
out_csv = OUTPUT_DIR / f"player-data-{scan_type}.csv"
checkpoint = CHECKPOINT_DIR /"full.txt"
download_players(url_file, out_csv, ROW_HEADER, checkpoint)



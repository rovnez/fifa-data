

# load the player urls

import logging
import typer

from player_url_loader import load_player_urls

from config import BASE_DIR


FILES_DIR = BASE_DIR / "files"
OUTPUT_DIR = BASE_DIR / "output"
CHECKPOINT_DIR = BASE_DIR / ".checkpoints"
CHECKPOINT_DIR.mkdir(exist_ok=True)

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(name)s: %(message)s")

scan_type = 'test'
path = FILES_DIR / f"player-urls-{scan_type}.csv"
load_player_urls(scan_type, path)
typer.echo(f"Wrote {path}")

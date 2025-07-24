# main.py
import logging
from pathlib import Path
import typer

from player_url_loader import load_player_urls
from downloader import download_players
from constants import ROW_HEADER  # same header as JS
from config import BASE_DIR

app = typer.Typer()

FILES_DIR = BASE_DIR / "files"
OUTPUT_DIR = BASE_DIR / "output"
CHECKPOINT_DIR = BASE_DIR / ".checkpoints"
CHECKPOINT_DIR.mkdir(exist_ok=True)

logging.basicConfig(level=logging.INFO,
                    format="%(asctime)s %(levelname)s %(name)s: %(message)s")


@app.command()
def download_urls(scan_type: str = typer.Option("full", help="full|test")):
    path = FILES_DIR / f"player-urls-{scan_type}.csv"
    load_player_urls(scan_type, path)
    typer.echo(f"Wrote {path}")


@app.command()
def full():
    url_file = FILES_DIR / "player-urls-full.csv"
    out_csv = OUTPUT_DIR / "player-data-full.csv"
    checkpoint = CHECKPOINT_DIR / "full.txt"
    download_players(url_file, out_csv, ROW_HEADER, checkpoint)


@app.command()
def test():
    url_file = FILES_DIR / "player-urls-test.csv"
    out_csv = OUTPUT_DIR / "player-data-test.csv"
    checkpoint = CHECKPOINT_DIR / "test.txt"
    download_players(url_file, out_csv, ROW_HEADER, checkpoint)
    # trivial assertions as in JS
    content = out_csv.read_text()
    assert "2000-07-21" in content
    assert "1998-12-20" in content
    typer.echo("all tests pass ✅")


if __name__ == "__main__":
    app()

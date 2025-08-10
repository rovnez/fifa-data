from pathlib import Path
import datetime
import time
from fifa_data.config import HTML_FILES_DIR


def load_html():
    """Load an html file

    Returns:

    """
    pass


def load_html_from_dir(filename: str):
    file_path = Path(HTML_FILES_DIR) / filename
    with open(file_path, "r", encoding="utf-8") as f:
        html_file = f.read()
    return html_file


def load_html_from_web(url): ...


def create_batch_name(batch_name: str = None) -> str:
    if not batch_name:
        batch_name = datetime.datetime.now(datetime.timezone.utc).strftime('%Y-%m-%d %H:%M:%S.%f')[:-3]
    return batch_name


def parse_player_url(player_url: str) -> dict:
    parts = [p for p in player_url.split("/") if p.isdigit()]
    return {
        "player_id": parts[0],
        "fifa_version": parts[1][:2],
        "fifa_update": parts[1][4:],
    }


def wait_with_progress_bar(seconds: int, length: int = 50):
    interval = 2
    for elapsed in range(seconds):
        filled = int(length * (elapsed + 1) / seconds)
        bar = '█' * filled + '-' * (length - filled)
        percent = f"{100 * (elapsed + 1) / seconds:.1f}"
        print(f'\rWaiting: |{bar}| {percent}% ({elapsed + 1}s/{seconds}s)', end='')
        time.sleep(interval)
    print()  # Move to next line when done


def convert_date_to_iso(date_text: str, date_format="%b %d, %Y") -> str:
    """
    Most dates are of the format "Jul 16, 2023" (<- format: "%b %d, %Y")
    We convert this to the ISO 8601 standard (i.e., '2023-07-16')

    Args:
        date_text: "Jul 16, 2023"
        date_format: "%b %d, %Y"

    Returns:
        Date in ISO 8601 format

    """
    return datetime.datetime.strptime(date_text, date_format).date().isoformat()

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



def wait_with_progress_bar(seconds: int, length: int = 50):
    interval = 1
    for elapsed in range(seconds):
        filled = int(length * (elapsed + 1) / seconds)
        bar = '█' * filled + '-' * (length - filled)
        percent = f"{100 * (elapsed + 1) / seconds:.1f}"
        print(f'\rWaiting: |{bar}| {percent}% ({elapsed + 1}s/{seconds}s)', end='')
        time.sleep(interval)
    print()  # Move to next line when done
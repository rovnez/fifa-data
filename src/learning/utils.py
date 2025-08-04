from pathlib import Path

from bs4 import BeautifulSoup

HTML_CACHE_DIR = "C:\\Users\\bokla\\020_Areas\\data\\fifa-data\\src\\learning\\html_cache"


def load_html_from_cache(name: str):
    file_path = Path(HTML_CACHE_DIR) / name
    with open(file_path, "r", encoding="utf-8") as f:
        html_file = f.read()
    return BeautifulSoup(html_file, 'html.parser')


def write_html_to_cache(html: BeautifulSoup, name: str, overwrite: bool = False):
    file_path = Path(HTML_CACHE_DIR) / name
    if file_path.exists() and not overwrite:
        print("File already exists")
        return
    else:
        file_path.write_text(str(html), encoding="utf-8", newline="\n")



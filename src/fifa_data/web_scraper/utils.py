from pathlib import Path


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

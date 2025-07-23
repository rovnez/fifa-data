import csv
from pathlib import Path
import os
import tempfile
from datetime import datetime


def format_date(date_str):
    try:
        return datetime.strptime(date_str.strip(), "%b %d, %Y").strftime("%Y-%m-%d")
    except Exception:
        return ""


def atomic_append(csv_path: Path, row_or_header):
    csv_path.parent.mkdir(parents=True, exist_ok=True)
    tmp_fd, tmp_name = tempfile.mkstemp(dir=csv_path.parent, prefix=csv_path.name, text=True)
    os.close(tmp_fd)
    try:
        # copy existing file or create
        if csv_path.exists():
            with csv_path.open("r", newline="", encoding="utf-8") as src, open(tmp_name, "w", newline="", encoding="utf-8") as dst:
                for line in src:
                    dst.write(line)
        # append
        with open(tmp_name, "a", newline="", encoding="utf-8") as f:
            writer = csv.writer(f, quoting=csv.QUOTE_ALL)
            if isinstance(row_or_header, list):
                writer.writerow(row_or_header)
            else:
                writer.writerow(row_or_header)  # in case header is tuple
        os.replace(tmp_name, csv_path)
    finally:
        if os.path.exists(tmp_name):
            os.remove(tmp_name)

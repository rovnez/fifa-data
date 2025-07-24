from bs4 import BeautifulSoup
from fifa_data.webscrape.scraper import get_page_content

BASE_URL = "https://sofifa.com"
PLAYER_LIST_URL = BASE_URL + "/players?col=oa&sort=desc&offset="


def get_player_urls(scan_size: int = 10) -> dict:
    offset = 0
    while True:
        html = get_page_content(PLAYER_LIST_URL + str(offset))
        soup = BeautifulSoup(html, "html.parser")
        players = soup.select("main article table tbody tr")
        if not players:
            break
        for row in players:
            href = row.find("a")["href"]
            f.write(BASE_URL + href + "\n")
        print(f"Downloaded player URLs count: {offset + 60}")
        if scan_type == "test":
            break
        next_link = soup.select_one(".pagination a:contains('Next')")
        if not next_link:
            break
        offset += 60


def load_player_urls(scan_type="test", output_path="files/player-urls-full.csv"):
    with open(output_path, "w") as f:
        offset = 0
        while True:
            html = get_page_content(PLAYER_LIST_URL + str(offset))
            soup = BeautifulSoup(html, "html.parser")
            players = soup.select("main article table tbody tr")
            if not players:
                break
            for row in players:
                href = row.find("a")["href"]
                f.write(BASE_URL + href + "\n")
            print(f"Downloaded player URLs count: {offset + 60}")
            if scan_type == "test":
                break
            next_link = soup.select_one(".pagination a:contains('Next')")
            if not next_link:
                break
            offset += 60

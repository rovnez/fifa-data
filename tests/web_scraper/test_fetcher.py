from fifa_data.web_scraper.fetcher import CurlFetcher



def test_fetch_urls():
    URL = "https://sofifa.com/players?col=vl&sort=desc&offset=0"
    fetcher = CurlFetcher()
    fetcher.get_page_content(URL)


test_fetch_urls()
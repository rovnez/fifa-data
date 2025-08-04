import bs4
import re


def parse_html_urls(html_str: str) -> list:
    soup = bs4.BeautifulSoup(html_str)
    sup = soup.article.table.find('tbody')
    ret = sup.find_all('a', href=re.compile('player/'))
    urls = [x.attrs['href'] for x in ret]
    return urls

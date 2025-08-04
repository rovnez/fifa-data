from urllib.request import urlopen

from learning.utils import load_html_from_cache, write_html_to_cache

from bs4 import BeautifulSoup

# html = urlopen('https://en.wikipedia.org/wiki/Ruud_van_Nistelrooy')
# write_html_to_cache(BeautifulSoup(html), name='ruud.html', overwrite=True)


bs = load_html_from_cache('ruud.html')

for link in bs.find_all('a'):
    if 'href' in link.attrs:
        print(link.attrs['href'])

from urllib.request import urlopen
from bs4 import BeautifulSoup
import datetime
import random
import re

random.seed(int(datetime.datetime.now().timestamp()))


def getLinks(articleUrl):
    html = urlopen('http://en.wikipedia.org{}'.format(articleUrl))
    bs = BeautifulSoup(html, 'html.parser')
    return bs.find('div', {'id': 'bodyContent'}).find_all('a', href=re.compile('^(/wiki/)((?!:).)*$'))


links = getLinks('/wiki/Ruud_van_Nistelrooy')
while len(links) > 0:
    newArticle = links[random.randint(0, len(links) - 1)].attrs['href']
    print(newArticle)
    links = getLinks(newArticle)

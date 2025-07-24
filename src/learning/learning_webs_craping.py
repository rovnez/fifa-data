

from urllib.request import urlopen
from urllib.error import HTTPError, URLError
from bs4 import BeautifulSoup

try:
    html = urlopen('http://pythonscraping.com/pages/page1.html')
except HTTPError as e:
    print(e)
except URLError as e:
    print("The server could not be found!")
else:
    bs = BeautifulSoup(html.read(), 'lxml')
    print("It worked:)")

    try:
        content = bs.head.title
    except AttributeError as e:
        print("Main tag was not found")
    else:
        if not content:
            print("Detail tag was not found")
        else:
            print(content)


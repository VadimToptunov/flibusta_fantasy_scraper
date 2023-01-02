import asyncio

import requests
from bs4 import BeautifulSoup
from tqdm import tqdm

URL = "http://flibusta.site/makebooklist?ab=ab1&g=sf_action,sf_epic,sf_heroic,sf_detective,sf_cyberpunk,sf_space," \
      "sf_social,sf_humor,sf_fantasy,sf,sf_fantasy_city,sf_postapocalyptic,sf_etc,russian_fantasy,sf_technofantasy," \
      "fairy_fantasy,sf_stimpank,popadancy&e=fb2&lng=ru&sort=sd2&= "


async def request_flibusta():
    session = requests.Session()
    resp_text = session.get(URL).text

    last_page_li = get_soup(resp_text).find("li", {"class": "pager-last"})
    last_page = int(last_page_li.find("a")["href"].split("(")[-1].replace("(", "").replace(")", ""))
    for page in tqdm(range(1, last_page + 1)):
        await scrape_page(page, session)


async def scrape_page(page, session):
    page_url = f"http://flibusta.site/makebooklist?ab=ab1&page={page}&g=sf_action,sf_epic,sf_heroic,sf_detective,sf_cyberpunk,sf_space,sf_social,sf_humor,sf_fantasy,sf,sf_fantasy_city,sf_postapocalyptic,sf_etc,russian_fantasy,sf_technofantasy,fairy_fantasy,sf_stimpank,popadancy&e=fb2&lng=ru&sort=sd2&="
    req_text = session.get(page_url).text
    fb2_books = get_soup(req_text).find_all("a", href=lambda
        href: href and "/b/" in href and "/read" not in href and "epub" not in href and "mobi" not in href)
    for book in fb2_books:
        if "fb2" not in book["href"]:
            download_link = f"http://flibusta.site{book['href']}/fb2"
            download_file(download_link, session, book.text)
            pass


def download_file(url, session, bookname):
    with session.get(url, allow_redirects=True, stream=True) as r:
        print(bookname)
        if r.status_code != 500:
            with open(f"flibusta/{bookname}.fb2", 'wb') as f:
                for chunk in r.iter_content(chunk_size=8192):
                    f.write(chunk)
        else:
            pass


def get_soup(resp_text):
    return BeautifulSoup(resp_text, "html.parser")


if __name__ == "__main__":
    asyncio.run(request_flibusta())

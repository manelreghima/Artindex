import os
import re
from multiprocessing import Pool
from time import sleep

import dotenv
import requests
import bs4
import lxml
import string

from lxml import etree
from tqdm.contrib.telegram import tqdm

from core.telegram import log

dotenv.read_dotenv()

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "core.settings")

import django

django.setup()

from lots.models import Art

DEFAULT_SEARCH_URL = "https://bidtoart.com/advanced-search?filter=art&title={key}"
DEFAULT_SEARCH_PAGE_URL = "https://bidtoart.com/advanced-search?filter=art&title={key}&page={page}"

# Regex for "395652 S ARE FOUND"
PAGE_INFO_REGEX = r"(\d+).*"
PAGE_INFO_XPATH = '//h5'

LOT_ROW_XPATH = '//tr[contains(@onmouseout, "Mouse")]'


def save_page(*args):
    page_num, key = args[0][0], args[0][1]
    url = DEFAULT_SEARCH_PAGE_URL.format(key=key, page=page_num)
    resp = requests.get(url)
    soup = bs4.BeautifulSoup(resp.text, 'lxml')
    arts = soup.findAll("div", {"class": "masonry-item"})
    art_objects = []

    for art in arts:
        a_tag = art.find("a")
        artist_tag = art.find("a", {"class": "artist-name"})
        technology_tag = art.find("span", {"class": "medium"})
        dimensions_tag = art.find("span", {"class": "dimension"})

        art_objects.append(Art(
            url=a_tag.attrs['href'],
            letter=key,
            page=page_num,
            title=a_tag.attrs['title'],
            artist=artist_tag.text.strip() if artist_tag else None,
            technology=technology_tag.text.strip() if technology_tag else None,
            dimensions=dimensions_tag.text.strip().replace("\n          ", " ") if dimensions_tag else None,
        ))

    Art.objects.bulk_create(art_objects, ignore_conflicts=True)


trans = str.maketrans(string.ascii_lowercase, string.ascii_lowercase[1:] + "a")

if __name__ == "__main__":
    log("[Bid To Art] First stage started")
    for letter in string.ascii_lowercase:
        next_letter = letter.translate(trans)

        # If lots with next letter more than 5000, then skip
        if Art.objects.filter(letter=next_letter).count() > 5000 and next_letter != "a":
            log(f"[Bid To Art] Skipping letter: {letter}, because {next_letter!r} exists")
            sleep(1)
            continue

        log(f"[Bid To Art] Scraping letter: {letter}")

        response = requests.get(DEFAULT_SEARCH_URL.format(key=letter))
        tree = etree.HTML(response.text)
        page_info = tree.xpath(PAGE_INFO_XPATH)[0].text.strip().replace(",", "")

        total_results = int(re.findall(PAGE_INFO_REGEX, page_info)[0])
        total_pages = total_results // 20

        lot_amount = Art.objects.filter(letter=letter).count()

        # If lot amount is greater than total results by 95% or more, skip
        if lot_amount > total_results * 0.95:
            log(f"[Bid To Art] Skipping letter: {letter}, because art amount is greater than total results by 95% or more")
            sleep(1)
            continue

        # Get the latest page
        latest_page = lot_amount // 30 + 1

        if latest_page > 1:
            log(f"[Bid To Art] Total pages: {total_pages}, latest page: {latest_page}")

        gen_args = [(page, letter) for page in range(latest_page, total_pages + 1)]

        with Pool(40) as p:
            list(tqdm(
                p.imap(save_page, gen_args),
                total=total_pages - latest_page + 1,
                desc=f"[Bid To Art] Scraping progress",
                token=os.getenv("TELEGRAM_TOKEN"),
                chat_id=os.getenv("TELEGRAM_CHAT_ID"),
                mininterval=5,
            ))

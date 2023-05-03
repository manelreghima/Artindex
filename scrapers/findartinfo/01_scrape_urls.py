import os
import re
from multiprocessing import Pool

import requests
import bs4
import lxml
import string

from lxml import etree
from tqdm import tqdm

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "core.settings")

import django
django.setup()

from lots.models import Lot
from core.telegram import log


DEFAULT_SEARCH_URL = "http://www.findartinfo.com/english/Artists/Result?artistName={key}"
DEFAULT_SEARCH_PAGE_URL = "http://www.findartinfo.com/english/Artists/Result?artistName={key}&pageIndex={page}"

# Regex for "339,821 results are found | Page 1 of 11,328 (max. 30 results pr. page)"
PAGE_INFO_REGEX = r"(\d+) .*of (\d+)"
PAGE_INFO_XPATH = '//h2'

LOT_ROW_XPATH = '//tr[contains(@onmouseout, "Mouse")]'


def save_page(*args):
    page_num, key = args[0][0], args[0][1]
    url = DEFAULT_SEARCH_PAGE_URL.format(key=key, page=page_num)
    resp = requests.get(url)
    soup = bs4.BeautifulSoup(resp.text, 'lxml')
    lots = soup.findAll("tr", {"onmouseout": "MouseMove(this,'out')"})

    for lot in lots:
        urls = lot.findAll("a")
        try:
            Lot.objects.create(
                url=urls[0].get("href"),
                letter=key,
                page=page_num,
                hammer_amount=urls[1].text,
                photo_amount=urls[2].text,
                sign_amount=urls[3].text,
                hammer_url=urls[1].get("href"),
                photo_url=urls[2].get("href"),
                sign_url=urls[3].get("href"),
            )

        except Exception as e:
            continue


trans = str.maketrans(string.ascii_lowercase, string.ascii_lowercase[1:] + "a")

if __name__ == "__main__":
    for letter in string.ascii_lowercase:
        next_letter = letter.translate(trans)

        # If lots with next letter more than 5000, then skip
        if Lot.objects.filter(letter=next_letter).count() > 5000 and next_letter != "a":
            log(f"Skipping letter: {letter}, because {next_letter!r} exists")
            continue

        log(f"Scraping letter: {letter}")

        response = requests.get(DEFAULT_SEARCH_URL.format(key=letter))
        tree = etree.HTML(response.text)
        page_info = tree.xpath(PAGE_INFO_XPATH)[0].text.strip().replace(",", "")

        total_results, total_pages = re.findall(PAGE_INFO_REGEX, page_info)[0]
        total_results = int(total_results)
        total_pages = int(total_pages)

        lot_amount = Lot.objects.filter(letter=letter).count()

        # If lot amount is greater than total results by 95% or more, skip
        if lot_amount > total_results * 0.95:
            log(f"Skipping letter: {letter}, because lot amount is greater than total results by 95% or more")
            continue

        # Get the latest page
        latest_page = lot_amount // 30 + 1

        gen_args = [(page, letter) for page in range(latest_page, total_pages + 1)]

        with Pool(40) as p:
            list(tqdm(p.imap(save_page, gen_args), total=total_pages - latest_page + 1))

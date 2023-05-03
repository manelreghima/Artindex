import os
import re
import uuid
from multiprocessing import Pool
from urllib.parse import urljoin

import requests
import bs4
import lxml
import string
import dotenv

from django.db import transaction
from lxml import etree
# from tqdm.contrib.telegram import tqdm
from tqdm import tqdm

dotenv.read_dotenv()

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "core.settings")

import django
django.setup()

from lots.models import Lot, Item
from core.telegram import log


BASE_URL = "http://www.findartinfo.com"


def download_lot(lot):
    if lot.has_lot_downloaded:
        return

    lot_url = urljoin(BASE_URL, lot.url)

    while True:
        resp = requests.get(lot_url)
        soup = bs4.BeautifulSoup(resp.text, 'lxml')
        tree = etree.HTML(str(soup))

        contents = soup.find("table", {"id": "table5"})

        if contents is None:
            break

        raw_author = contents.find("h1", {"class": "underline"}).text
        author = raw_author.replace("Art auction result for", "").strip() if raw_author else None

        lot_table = contents.findAll("table")[1]
        items = lot_table.findAll("tr")[1:-1]

        instances = []

        for item in items:
            tds = item.findAll("td")
            if not tds or len(tds) < 6:
                continue

            auction_date = tds[1].text.strip()
            title = tds[2].text.strip()
            size = tds[3].text.strip()
            technique = tds[4].text.strip()
            price = tds[5].text.strip()

            instances.append(Item(
                lot=lot,
                auction_date=auction_date,
                title=title,
                dimensions=size,
                technique=technique,
                start_price=price,
                author=author,
            ))

        Item.objects.bulk_create(instances)

        next_page_button = tree.xpath('//a[contains(text(), ">")]')
        if next_page_button:
            lot_url = urljoin(BASE_URL, next_page_button[0].get("href"))
            continue

        break

    lot.has_lot_downloaded = True
    lot.save()


if __name__ == "__main__":
    lots = Lot.objects.filter(hammer_amount__gt=0, has_lot_downloaded=False)
    log(f"[FINDARTINFO] Stage 2: Total {lots.count()} lots to download")

    PROCESSES = 30

    # Estimate time in hours to download all lots
    # Running 30 processes, each process takes from 1 to 30 seconds to download 1 lot
    estimate_min = (lots.count() / PROCESSES) * 30 / 60 / 60
    estimate_max = (lots.count() / PROCESSES) / 60 / 60

    log(f"[FINDARTINFO] Stage 2: Estimated time: from {estimate_max:.2f} to {estimate_min:.2f} hours")

    with Pool(PROCESSES) as p:
        list(tqdm(
            p.imap_unordered(download_lot, lots),
            total=lots.count(),
            desc=f"[FINDARTINFO] Scraping progress",
            # token=os.getenv("TELEGRAM_TOKEN"),
            # chat_id=os.getenv("TELEGRAM_CHAT_ID"),
            # mininterval=5,
        ))

    log(f"[FINDARTINFO] Stage 2: Done")

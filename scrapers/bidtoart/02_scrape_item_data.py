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
dotenv.read_dotenv()

from django.db import transaction
from lxml import etree
from tqdm.contrib.telegram import tqdm

from core.telegram import log

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "core.settings")

import django
django.setup()

from lots.models import Art


def scrape_information(art):
    art.scrape()


if __name__ == "__main__":
    arts = Art.objects.filter(has_info_downloaded=False, is_scraped=False)

    log(f"[BIDTOART] Stage 2: Scraping {arts.count()} arts")

    with Pool(40) as p:
        list(tqdm(
            p.imap(scrape_information, arts),
            total=arts.count(),
            desc=f"[BIDTOART] Scraping progress",
            token=os.getenv("TELEGRAM_TOKEN"),
            chat_id=os.getenv("TELEGRAM_CHAT_ID"),
            mininterval=5,
            ))

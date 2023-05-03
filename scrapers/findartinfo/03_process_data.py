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


def prettify_item(item):
    item.prettify()


if __name__ == "__main__":
    items = Item.objects.filter(prettified=False)
    log(f"[FINDARTINFO] Stage 3: Total {items.count()} items to prettify. Estimated time: {items.count() / 200 / 60 / 60:2f} hours.")

    if not items.exists():
        log("[FINDARTINFO] No items to prettify.")
        exit()

    for item in tqdm(
            items,
            total=items.count(),
            desc=f"[FINDARTINFO] Prettifying items",
            # token=os.getenv("TELEGRAM_TOKEN"),
            # chat_id=os.getenv("TELEGRAM_CHAT_ID"),
            # mininterval=1,
        ):
        item.prettify()

    log(f"[FINDARTINFO] Done prettifying {items.count()} items.")

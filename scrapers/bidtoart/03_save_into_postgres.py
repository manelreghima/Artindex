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
import psycopg2

from django.db import transaction
from django.core.paginator import Paginator
from lxml import etree
# from tqdm.contrib.telegram import tqdm
from tqdm import tqdm

dotenv.read_dotenv()

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "core.settings")

import django
django.setup()

from lots.models import Art
from core.telegram import log


DATABASE_NAME = os.getenv("DATABASE_NAME")
CONNECTION = psycopg2.connect(
    f"dbname={DATABASE_NAME} user=postgres"
)
CONNECTION.autocommit = True
CURSOR = CONNECTION.cursor()


def save_into_postgres(items):
    sql = "\n".join([item.postgres_insert_query for item in items])
    CURSOR.execute(sql)


if __name__ == "__main__":
    page_amount = 100
    arts = Art.objects.filter(has_info_downloaded=True, is_scraped=True)
    log(f"[BIDTOART] Stage 4: Total {arts.count()} arts to save into postgres.\n"
    f"Estimated time: {arts.count() / 4 / page_amount / 60 :2f} minutes.")

    p = Paginator(arts, page_amount)

    for page in tqdm(p.page_range):
        save_into_postgres(p.page(page).object_list)

    log("[BIDTOART] Stage 4: Done.")

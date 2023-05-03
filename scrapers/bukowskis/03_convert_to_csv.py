"""This script was created for scraping dowloaded html files and saving them to the csv file.
"""

# Prepare Django
import os
import csv
from concurrent.futures import ThreadPoolExecutor, as_completed
from multiprocessing.pool import ThreadPool, Pool

from tqdm import tqdm
import django
from tqdm_multi_thread import TqdmMultiThreadFactory

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from data.services.items import ItemParser

# Import Django models
from data.models import Item


def get_csv_row(item):
    return ItemParser(item).csv_row


if __name__ == "__main__":
    # Iterate items
    items = Item.objects.filter(is_file_exists=True)
    total = items.count()
    print(f"Total {total} will be converted to csv.")

    HEADER = ["auction_date", "author", "start_price", "end_price", "currency", "lifetime", "category", "description"]

    csv_file = "data.csv"
    with open(csv_file, "w", encoding="utf-8", newline="") as f:
        writer = csv.writer(f, delimiter=",")
        writer.writerow(HEADER)
        with Pool(60) as p:
            r = list(tqdm(p.imap_unordered(get_csv_row, items), total=total))

        writer.writerows(r)

    print(f"Saved {total} items to {csv_file}.")

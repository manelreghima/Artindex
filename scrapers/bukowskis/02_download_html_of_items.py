"""This script was created for downloading lots from Bukowskis.com
and saving them to the database.

It will download the html of each lot and save it into the file."""

# Prepare Django
import os
from concurrent.futures import ThreadPoolExecutor, as_completed
from multiprocessing.pool import ThreadPool, Pool

from tqdm import tqdm
import django
from tqdm_multi_thread import TqdmMultiThreadFactory

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

# Import Django models
from data.models import Item

# Import Bukowskis.com scraping services
from data.services.items import BaseItem, save_file_to_disk

ERROR_FILE = "02_error_{id}.html"


def download_and_save_item(item):
    result = BaseItem(item).get_contents_to_save()
    try:
        if result:
            save_file_to_disk(item, result)

        else:
            raise Exception("No contents")

    except Exception as e:
        file = ERROR_FILE.format(id=item.lot_id)
        with open(file, "w", encoding="utf-8") as f:
            f.write(e)


if __name__ == "__main__":
    # Iterate items
    items = Item.objects.filter(is_file_exists=False)
    total = items.count()
    print(f"Found {total} items to download.")

    with Pool(20) as p:
        r = list(tqdm(p.imap_unordered(download_and_save_item, items), total=total))

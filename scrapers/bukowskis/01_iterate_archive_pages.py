"""This script was created for downloading lots from Bukowskis.com
and saving them to the database.

It will scrape the art archive page and store all lot ids in the database."""


# Prepare Django
import os
import time

import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

# Import Django models

# Import Bukowskis.com scraping services
from data.services.pages import ArchiveArtPage, save_ids_to_database

ERROR_FILE = "01_error_{page}.html"


if __name__ == "__main__":
    # Iterate archive pages
    page = ArchiveArtPage(1)
    while page.has_next_page:
        time.sleep(0.2)
        print("Saving page: {page}. ".format(page=page.page))

        if len(page.item_ids) == 0:
            file = ERROR_FILE.format(page=page.page)
            print(f"No items on page: {page.page}. Saving the response into file {file}")
            with open(file, "w", encoding="utf-8") as f:
                f.write(page.soup.prettify(formatter="html5"))
            break

        created = save_ids_to_database(page.item_ids_and_urls)
        print(f"Created {created} of {len(page.item_ids)} items.")
        page = ArchiveArtPage(page.page + 1)

    else:
        print("Saving last page: {page}. ".format(page=page.page))
        created = save_ids_to_database(page.item_ids_and_urls)
        print(f"Created {created} of {len(page.item_ids)} items.")

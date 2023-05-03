import os

import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from data.models import Item

from data.services.pages import ArchiveArtPage
from data.services.items import BaseItem, ItemParser


if __name__ == "__main__":
    # order by random
    item = Item.objects.filter(is_file_exists=True, lot_id="1441867").order_by('?').first()
    parser = ItemParser(item)
    ...

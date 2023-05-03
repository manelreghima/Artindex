import os
from urllib.parse import urljoin

from django.conf import settings
from django.db import models


class Item(models.Model):
    lot_id = models.IntegerField()
    url = models.URLField(null=True, blank=True)
    is_file_exists = models.BooleanField(default=False)

    @property
    def lot_url(self) -> str:
        return urljoin("https://www.bukowskis.com/", self.url)

    @property
    def lot_file(self) -> str:
        return os.path.join(settings.BASE_DIR, "data", "lots", "{lot_id}.html".format(lot_id=self.lot_id))

    @property
    def lot_file_exists(self) -> bool:
        return os.path.exists(self.lot_file)


class ItemCategory(models.Model):
    item = models.ForeignKey(Item, on_delete=models.CASCADE)
    category = models.CharField(max_length=255)

import math

from django.db import models


class Lot(models.Model):
    url = models.URLField(unique=True)
    file = models.FileField(upload_to='lots', null=True, blank=True)

    letter = models.CharField(max_length=1, null=True, blank=True)
    page = models.IntegerField(null=True, blank=True)

    hammer_amount = models.IntegerField()
    photo_amount = models.IntegerField()
    sign_amount = models.IntegerField()

    hammer_url = models.URLField()
    photo_url = models.URLField()
    sign_url = models.URLField()

    has_lot_downloaded = models.BooleanField(default=False)


class Item(models.Model):
    lot = models.ForeignKey(Lot, on_delete=models.CASCADE)
    auction_date = models.CharField(max_length=255, null=True, blank=True)
    auction_year = models.CharField(max_length=255, null=True, blank=True)
    author = models.CharField(max_length=255, null=True, blank=True)
    title = models.CharField(max_length=1024, null=True, blank=True)
    start_price = models.CharField(max_length=255, null=True, blank=True)
    end_price = models.CharField(max_length=255, null=True, blank=True)
    currency = models.CharField(max_length=255, null=True, blank=True)
    decade = models.CharField(max_length=255, null=True, blank=True)
    technique = models.CharField(max_length=255, null=True, blank=True)
    dimensions = models.CharField(max_length=255, null=True, blank=True)
    area = models.CharField(max_length=255, null=True, blank=True)

    prettified = models.BooleanField(default=False)

    def prettify(self):
        if self.prettified:
            return True

        if self.auction_date:
            self.auction_year = self.auction_date.split('-')[-1]
            self.decade = self.auction_year[:3] + '0'

        if self.start_price == 'Unsold':
            self.start_price = '0'
            self.end_price = '0'

        elif self.start_price:
            price = self.start_price.split(' ')
            self.start_price = price[0].replace(',', '') if len(price) > 0 else '0'
            self.end_price = self.start_price
            self.currency = price[1] if len(price) > 1 else None

        if self.dimensions:
            # ex. 7.28 x 4.72 in
            dimensions = self.dimensions.replace(" in", "").split('x')
            self.area = str(math.prod([float(d) for d in dimensions] + [2.54]))

        self.prettified = True
        self.save()

    def __str__(self):
        return f"{self.title} by {self.author} ({self.auction_date})"

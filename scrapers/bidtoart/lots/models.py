import re
from urllib.parse import urljoin

import math
import requests
import bs4

from django.db import models


class Art(models.Model):
    BASE_URL = "https://bidtoart.com"
    url = models.URLField(default="")

    letter = models.CharField(max_length=1, null=True, blank=True)
    page = models.IntegerField(null=True, blank=True)

    title = models.CharField(max_length=255, null=True, blank=True)
    artist = models.CharField(max_length=255, null=True, blank=True)
    technology = models.CharField(max_length=255, null=True, blank=True)
    dimensions = models.CharField(max_length=255, null=True, blank=True)

    auction_date = models.CharField(max_length=255, null=True, blank=True)
    auction_year = models.CharField(max_length=255, null=True, blank=True)
    start_price = models.CharField(max_length=255, null=True, blank=True)
    end_price = models.CharField(max_length=255, null=True, blank=True)
    currency = models.CharField(max_length=255, null=True, blank=True)
    decade = models.CharField(max_length=255, null=True, blank=True)
    source = models.CharField(max_length=255, null=True, blank=True)
    category = models.CharField(max_length=255, null=True, blank=True)

    has_info_downloaded = models.BooleanField(default=False)
    is_scraped = models.BooleanField(default=False)

    """
    --- Postgres create table
    CREATE TABLE items (
        id SERIAL PRIMARY KEY,
        auction_date VARCHAR(1024),
        auction_year VARCHAR(1024),
        author VARCHAR(1024),
        title VARCHAR(1024),
        start_price VARCHAR(1024),
        end_price VARCHAR(1024),
        currency VARCHAR(1024),
        decade VARCHAR(1024),
        technique VARCHAR(1024),
        source VARCHAR(1024),
        dimension VARCHAR(1024)
    );
    
    ALTER SEQUENCE items_id_seq RESTART WITH 1;"""

    @property
    def author(self):
        return self.artist

    @property
    def technique(self):
        return self.technology

    @property
    def area(self):
        # 1.4 cm - 93.8 cm (0.55 in - 36.93 in)
        # regex for 1.4 cm - 93.8 cm to get 1.4 and 93.8
        res = re.findall(r"\d+\.\d+", self.dimensions)
        # return multiplication of 1.4 and 93.8
        return math.prod([float(x) for x in res])

    @property
    def full_url(self):
        return urljoin(self.BASE_URL, self.url)

    def scrape(self):
        r = requests.get(self.full_url)
        soup = bs4.BeautifulSoup(r.text, "lxml")

        info = soup.find("table", {"class": "product-info"})

        if info is None:
            self.has_info_downloaded = False
            self.is_scraped = True
            self.save()
            return

        trs = info.findAll("tr")

        skip_end_price = False

        for tr in trs:
            key = tr.find("td", {"class": "label"}).text.strip()
            value = tr.find("td", {"class": "value"}).text.strip()

            if not value:
                continue

            match key:
                case "Estimate:":
                    splitted = value.split("-")
                    min_price = splitted[0].strip()
                    max_price = splitted[1].strip() if len(splitted) > 1 else None

                    price = max_price or min_price

                    if not price:
                        break

                    # price like E100
                    self.currency = price[0]
                    self.start_price = price[1:]

                    if not skip_end_price:
                        self.end_price = self.start_price

                case "Auction date:":
                    self.auction_date = value
                    self.auction_year = value.split(",")[-1].strip()
                    self.decade = self.auction_year[:3] + "0"

                case "Auction house:":
                    self.source = value

                case "Category:":
                    self.category = value

                case "Price realised:":
                    skip_end_price = True
                    self.currency = value[0]
                    self.end_price = value[1:]

        self.has_info_downloaded = True
        self.is_scraped = True
        self.save()

    @property
    def safe_title(self):
        return self.title.replace("'", "''") if self.title else ''

    @property
    def safe_author(self):
        return self.author.replace("'", "''") if self.author else ''

    @property
    def safe_technique(self):
        return self.technology.replace("'", "''") if self.technology else ''

    @property
    def safe_source(self):
        return self.source.replace("'", "''") if self.source else ''
        
    @property
    def postgres_insert_query(self):
        return f"""INSERT INTO items (
            auction_date,
            auction_year,
            author,
            title,
            start_price,
            end_price,
            currency,
            decade,
            technique,
            source,
            dimension
        ) VALUES (
            '{self.auction_date}',
            '{self.auction_year}',
            '{self.safe_author}',
            '{self.safe_title}',
            '{self.start_price}',
            '{self.end_price}',
            '{self.currency}',
            '{self.decade}',
            '{self.safe_technique}',
            '{self.safe_source}',
            '{self.area}'
        );""".replace("None", "NULL")
    
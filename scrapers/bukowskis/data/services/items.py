from functools import cached_property

import bs4
import requests
from lxml import etree
from requests import Response

from data.models import Item
from data.services.classes import BaseRequestHandler


class BaseItem(BaseRequestHandler):
    URL = "https://www.bukowskis.com/en/lots/{lot_id}"

    def __init__(self, item: Item):
        self.item = item

    @cached_property
    def response(self) -> Response:
        """Get response

        :return: Response"""
        headers = {
            "User-Agent": self.faker.user_agent()
        }
        return requests.get(self.item.lot_url, headers=headers)

    def get_contents_to_save(self) -> str:
        """Get contents to save in html

        :return: str"""
        el = self.soup.findAll("div", {"class": "o-sheet"})
        return el[0].prettify() if el else ""


class ItemParser:
    def __init__(self, item: Item):
        self.item = item

    @cached_property
    def contents(self):
        """Get contents

        :return: str"""
        return open(self.item.lot_file, "r", encoding="utf-8").read()

    @cached_property
    def soup(self) -> bs4.BeautifulSoup:
        """Get soup

        :return: BeautifulSoup"""
        return bs4.BeautifulSoup(self.contents, "html.parser")

    @cached_property
    def etree(self) -> bs4.element.Tag:
        """Get etree

        :return: etree"""
        return etree.HTML(self.soup.prettify())

    @cached_property
    def category(self) -> str:
        """Get category

        :return: str"""
        return self.xpath_text("//div[@class='c-market-lot-show-navigation__category-and-id']//a", 1)

    @cached_property
    def author(self) -> str:
        """Get author

        :return: str"""
        return self.xpath_text("//h1[@class='c-lot-heading__title']")

    @cached_property
    def lifetime(self) -> str:
        """Get lifetime

        :return: str"""
        return self.xpath_text("//div[@class='c-lot-show-header__artist-lifetime']")

    @cached_property
    def hammer_price(self) -> str:
        """Get hammer price

        :return: str"""
        return self.xpath_text(
            "//div[contains(@class, 'c-market-lot-show-result__leading-amount')]").replace("\xa0", "") or self.estimate

    @cached_property
    def full_estimate(self) -> list:
        """Get full estimate

        :return: list"""
        return self.xpath_text("//div[@class='c-market-lot-show-estimate__amount']").rsplit('\xa0', 1)

    @cached_property
    def estimate(self) -> str:
        """Get estimate

        :return: str"""
        return self.full_estimate[0].replace("\xa0", "") if len(self.full_estimate) > 0 else ""

    @cached_property
    def currency(self) -> str:
        """Get currency

        :return: str"""
        return self.full_estimate[1] if len(self.full_estimate) > 1 else ""

    @cached_property
    def date_time(self) -> str:
        """Get date time

        :return: str"""
        el = self.etree.xpath("//time[@class='c-market-lot-show-bidding-end-date']")
        return el[0].attrib["datetime"] if el else ""

    @cached_property
    def description(self) -> str:
        """Get description

        :return: str"""
        return self.soup.find("div", {"class": "c-lot-description"}).text.strip()

    @cached_property
    def csv_row(self) -> list:
        """Get csv row

        :return: list"""
        return [
            self.date_time,
            self.author,
            self.estimate,
            self.hammer_price,
            self.currency,
            self.lifetime,
            self.category,
            self.description,
        ]

    def xpath_text(self, path, idx=0):
        el = self.etree.xpath(path)
        return el[idx].text.strip() if len(el) > idx else ""


def save_file_to_disk(item: Item, contents: str) -> None:
    """Save lot html to disk

    :param item: Item
    :param contents: str
    :return: None
    """

    with open(item.lot_file, "w", encoding="utf-8") as f:
        f.write(contents)
        item.is_file_exists = True
        item.save()

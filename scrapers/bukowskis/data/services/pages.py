from functools import cached_property

import bs4
import requests
from django.db import transaction
from faker import Faker
from requests import Response
from lxml import etree

from data.models import Item
from data.services.classes import BaseRequestHandler
from data.services.cookies import get_cookies


class BasePage(BaseRequestHandler):
    """Base Page class"""
    NEXT_PAGE_XPATH = "//a[@rel='next']"
    ITEM_XPATH = "//div[@class='c-lot-index__lots']//div[contains(@id, 'lot')]"
    URL = "https://bukowskis.com/en/lots/page/{page}"

    def __init__(self, page: int):
        self.page = page

    @cached_property
    def response(self) -> Response:
        """Get response

        :return: Response"""
        headers = {
            "User-Agent": self.faker.user_agent()
        }
        cookies = get_cookies()
        return requests.get(self.URL.format(page=self.page), headers=headers, cookies=cookies)

    @cached_property
    def html_items(self):
        """Get items

        :return: Items"""
        return self.etree.xpath(self.ITEM_XPATH)

    @property
    def item_ids(self) -> list:
        """Get item ids

        :return: list"""
        return [int(item.attrib["data-lot-id"]) for item in self.html_items if item and item.attrib["data-lot-id"]]

    @property
    def item_ids_and_urls(self) -> dict:
        """Get item ids and urls

        :return: dict"""
        return {
            int(item.attrib["data-lot-id"]): item.xpath(".//a")[0].attrib["href"]
            for item in self.html_items if item and item.attrib["data-lot-id"]
        }

    @cached_property
    def has_next_page(self) -> bool:
        """Check if page has next page

        :return: bool"""
        return bool(self.etree.xpath(self.NEXT_PAGE_XPATH))


class ArchiveArtPage(BasePage):
    URL = "https://www.bukowskis.com/en/lots/category/art/page/{page}/archive/yes"

    @cached_property
    def html_categories(self):
        """Get categories

        :return: Categories"""
        return self.etree.xpath("//ul[@class='c-search-filters__box'][1]//li/a")

    @property
    def categories(self) -> dict:
        """Get categories

        :return: Categories"""
        return {
            category.text.strip(): category.attrib["href"]
            for category in self.html_categories
        }


@transaction.atomic
def save_ids_to_database(lot_info: dict) -> int:
    """Save lot ids to database

    :param lot_info: dict
    :return: int Created items count"""

    created_count = 0

    for lot_id in lot_info:
        item, created = Item.objects.get_or_create(lot_id=lot_id, defaults={"url": lot_info[lot_id]})
        if created:
            created_count += 1

    return created_count

from functools import cached_property

import bs4
import requests
from faker import Faker
from lxml import etree
from requests import Response


class BaseRequestHandler:
    URL = "https://google.com/"

    @cached_property
    def faker(self):
        return Faker()

    @cached_property
    def response(self) -> Response:
        """Get response

        :return: Response"""
        headers = {
            "User-Agent": self.faker.user_agent()
        }
        return requests.get(self.URL, headers=headers)

    @property
    def content(self) -> str:
        """Get page content

        :return: str"""
        return self.response.text

    @property
    def soup(self) -> bs4.BeautifulSoup:
        """Get soup

        :return: BeautifulSoup"""
        return bs4.BeautifulSoup(self.content, "html.parser")

    @property
    def etree(self) -> bs4.element.Tag:
        """Get etree

        :return: etree"""
        return etree.HTML(self.soup.prettify())

    def __str__(self) -> str:
        return f"RequestHandler <url: {self.URL}>"

    def __repr__(self) -> str:
        return self.__str__()

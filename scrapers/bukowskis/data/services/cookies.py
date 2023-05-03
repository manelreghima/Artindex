import os

from django.conf import settings


def get_cookies() -> dict:
    """Opens cookies.txt and returns raw cookies as dict

    :return: dict"""
    with open(os.path.join(settings.BASE_DIR, 'cookies.txt'), "r", encoding="utf-8") as f:
        return {line.split("=")[0]: line.split("=")[1] for line in f.read().split(";")}

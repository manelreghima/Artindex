import os

from telegram import Bot


def log(message):
    bot = Bot(token=os.getenv("TELEGRAM_TOKEN"))
    print(message)
    bot.send_message(chat_id=os.getenv("TELEGRAM_CHAT_ID"), text=message)

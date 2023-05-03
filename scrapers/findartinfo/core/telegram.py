import os

from telegram import Bot


def log(message):
    print(message)
    try:
        bot = Bot(token=os.getenv("TELEGRAM_TOKEN"))
        bot.send_message(chat_id=os.getenv("TELEGRAM_CHAT_ID"), text=message)
    except:
        pass

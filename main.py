import os
import random
import requests
from asyncio import run
from telegram import Bot
from dotenv import load_dotenv


XKCD_CURRENT_URL = "https://xkcd.com/info.0.json"
XKCD_COMIC_URL_TEMPLATE = "https://xkcd.com/{comic_id}/info.0.json"
TEMP_FILENAME = "comic.png"


def fetch_total_comics_count():
    response = requests.get(XKCD_CURRENT_URL)
    response.raise_for_status()
    return response.json()["num"]


def fetch_comic(comic_id):
    comic_url = XKCD_COMIC_URL_TEMPLATE.format(comic_id=comic_id)
    response = requests.get(comic_url)
    response.raise_for_status()
    return response.json()


def download_image(url, filepath):
    response = requests.get(url)
    response.raise_for_status()
    with open(filepath, "wb") as file:
        file.write(response.content)


async def main():
    load_dotenv()
    bot_token = os.getenv("BOT_TOKEN")
    chat_id = os.getenv("CHAT_ID")

    if not bot_token:
        raise ValueError("Критическая ошибка: Переменная окружения BOT_TOKEN не задана.")
    if not chat_id:
        raise ValueError("Критическая ошибка: Переменная окружения CHAT_ID не задана.")

    total_comics = fetch_total_comics_count()
    comic_id = random.randint(1, total_comics)
    comic = fetch_comic(comic_id)

    try:
        download_image(comic["img"], TEMP_FILENAME)
        bot = Bot(token=bot_token)
        async with bot:
            with open(TEMP_FILENAME, "rb") as photo_file:
                await bot.send_photo(chat_id=chat_id, photo=photo_file, caption=comic["alt"])
    finally:
        if os.path.exists(TEMP_FILENAME):
            os.remove(TEMP_FILENAME)


if __name__ == "__main__":
    run(main())
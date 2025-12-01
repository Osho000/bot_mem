import os
import json
import random
from pathlib import Path
import asyncio

import schedule
from aiogram import Bot
from aiogram.types import FSInputFile
from datetime import datetime
import pytz


BOT_TOKEN = os.getenv("BOT_TOKEN") or "8566166980:AAHruD6CwhAx_F0POAysbrgcTQ4-rXckuFc"
CHANNEL_ID = os.getenv("CHANNEL_ID") or "-4892445169"
MEMES_FOLDER = "memes"
USED_JSON = "used.json"

bot = Bot(token=BOT_TOKEN)

def load_used():
    if not os.path.exists(USED_JSON):
        return []
    with open(USED_JSON, "r", encoding="utf-8") as f:
        return json.load(f)

def save_used(lst):
    with open(USED_JSON, "w", encoding="utf-8") as f:
        json.dump(lst, f, indent=2, ensure_ascii=False)

def pick_meme():
    folder = Path(MEMES_FOLDER)
    all_memes = [str(p) for p in folder.glob("*") if p.is_file()]
    if not all_memes:
        raise RuntimeError("Папка с мемами пуста!")

    used = load_used()
    unused = [m for m in all_memes if m not in used]

    if not unused:
        used = []
        save_used([])
        unused = all_memes

    meme = random.choice(unused)
    used.append(meme)
    save_used(used)
    return meme


async def post_meme():
    meme_path = pick_meme()
    photo = FSInputFile(meme_path)
    await bot.send_photo(chat_id=int(CHANNEL_ID), photo=photo, caption="Доброе утро! ☕️💼")


async def scheduled_job():
    tz = pytz.timezone("Europe/Moscow")
    now = datetime.now(tz)
    print(f"[{now.strftime('%Y-%m-%d %H:%M:%S')}] Отправка мемов...")
    await post_meme()

async def scheduler_loop():
    schedule.every().day.at("11:55").do(lambda: asyncio.create_task(scheduled_job()))

    while True:
        schedule.run_pending()
        await asyncio.sleep(1)


if __name__ == "__main__":
    try:
        asyncio.run(scheduler_loop())
    finally:
        asyncio.run(bot.session.close())

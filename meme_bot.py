import os
import json
import random
from pathlib import Path
import asyncio

from aiogram import Bot, Dispatcher
from aiogram.types import FSInputFile


BOT_TOKEN = os.getenv("BOT_TOKEN")
CHANNEL_ID =""
MEMES_FOLDER = "memes"
USED_JSON = "used.json"

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()


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


async def get_channel_id():
    updates = await bot.get_updates()
    for u in updates:
        if u.message and u.message.chat.type in ["channel", "supergroup", "group"]:
            print("Найден chat_id:", u.message.chat.id, "| title:", u.message.chat.title)
            return u.message.chat.id
    return None


async def post_meme(channel_id):
    meme_path = pick_meme()
    photo = FSInputFile(meme_path)
    await bot.send_photo(chat_id=int(channel_id), photo=photo, caption="Доброе утро! ☕️💼")



async def main():
    global CHANNEL_ID
    if not CHANNEL_ID:
        print("CHANNEL_ID не указан. Пытаемся найти через обновления...")
        CHANNEL_ID = await get_channel_id()
        if not CHANNEL_ID:
            raise ValueError(
                "Не удалось определить CHANNEL_ID автоматически. "
                "Добавьте бот в канал/группу и отправьте туда сообщение."
            )
        print(f"Автоматически найден CHANNEL_ID: {CHANNEL_ID}")



    try:
        await dp.start_polling(bot)
    finally:
        await bot.session.close()

if __name__ == "__main__":
    asyncio.run(main())

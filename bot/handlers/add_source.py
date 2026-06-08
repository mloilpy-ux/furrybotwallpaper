from aiogram import Router
from aiogram.types import Message
from aiogram.filters import Command
import aiosqlite
import re
from database.db import DB_PATH
from config import ADMIN_ID

router = Router()

@router.message(Command("add"))
async def add_source(m: Message):
    if m.from_user.id != ADMIN_ID:
        await m.answer("⛔ Только администратор может добавлять источники.")
        return
    
    try:
        args = m.text.split(maxsplit=1)
        if len(args) < 2:
            raise ValueError
        url = args[1].strip()
    except:
        await m.answer("Использование:\n/add https://reddit.com/r/subreddit\n/add https://t.me/channel")
        return
    
    # Определяем тип
    if "reddit.com" in url or "reddit.com/r/" in url:
        source_type = "reddit"
    elif "t.me" in url or url.startswith("@"):
        source_type = "telegram"
    else:
        await m.answer("❌ Поддерживаются только Reddit и Telegram на данный момент.")
        return
    
    # Красивое имя
    if source_type == "reddit":
        name = re.search(r'/r/([^/]+)', url)
        name = name.group(1) if name else "reddit_source"
    else:
        name = re.sub(r'https?://t\.me/|@', '', url).strip('/')
    
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute(
            "INSERT OR IGNORE INTO sources (name, url, type, added_by) VALUES (?,?,?,?)",
            (name, url, source_type, m.from_user.id)
        )
        await db.commit()
    
    await m.answer(f"✅ Источник добавлен!\nТип: {source_type}\nНазвание: {name}")

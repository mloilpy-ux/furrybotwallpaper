from aiogram import Router
from aiogram.types import Message
from aiogram.filters import Command
import aiosqlite, re
from database.db import DB_PATH
from config import ADMIN_ID

router = Router()

@router.message(Command("add"))
async def add(m: Message):
    if m.from_user.id != ADMIN_ID:
        await m.answer("⛔")
        return
    try:
        url = m.text.split(maxsplit=1)[1]
    except:
        await m.answer("Использование: /add ссылка")
        return
    
    t = None
    if "reddit.com" in url: t = "reddit"
    elif "t.me" in url or url.startswith("@"): t = "telegram"
    elif "twitter.com" in url or "x.com" in url: t = "twitter"
    
    if not t:
        await m.answer("❌")
        return
    
    name = re.sub(r'https?://[^/]+/', '', url).strip('/')
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute("INSERT OR IGNORE INTO sources (name, url, type, added_by) VALUES (?,?,?,?)", (name, url, t, m.from_user.id))
        await db.commit()
    await m.answer(f"✅ {t} добавлен")

from aiogram import Router
from aiogram.types import Message
from aiogram.filters import Command
from config import ADMIN_ID
import aiosqlite
from database.db import DB_PATH

router = Router()

@router.message(Command("add"))
async def add(m: Message):
    if m.from_user.id != ADMIN_ID:
        return
    try:
        url = m.text.split(maxsplit=1)[1]
        t = "reddit" if "reddit" in url else "telegram" if "t.me" in url else "twitter" if "x.com" in url else None
        if not t: return
        name = url.split("/")[-1]
        async with aiosqlite.connect(DB_PATH) as db:
            await db.execute("INSERT OR IGNORE INTO sources (name,url,type,added_by) VALUES (?,?,?,?)", (name, url, t, m.from_user.id))
            await db.commit()
        await m.answer("OK")
    except:
        await m.answer("use: /add url")

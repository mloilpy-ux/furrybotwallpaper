from aiogram import Router
from aiogram.types import Message
from aiogram.filters import Command
import aiosqlite

from database.db import DB_PATH

router = Router()

@router.message(Command("sources"))
async def cmd_sources(message: Message):
    async with aiosqlite.connect(DB_PATH) as db:
        cursor = await db.execute(
            "SELECT id, name, url, type, is_active FROM sources ORDER BY id DESC LIMIT 15"
        )
        sources = await cursor.fetchall()

    if not sources:
        await message.answer("У тебя пока нет добавленных источников.\nИспользуй /add")
        return

    text = "📋 <b>Твои источники:</b>\n\n"
    for src in sources:
        status = "✅" if src[4] else "❌"
        text += f"{status} <b>{src[1]}</b> ({src[3]})\n{src[2]}\n\n"

    await message.answer(text)
from aiogram import Router
from aiogram.types import Message
from aiogram.filters import Command
import aiosqlite
from database.db import DB_PATH
from config import ADMIN_ID

router = Router()

@router.message(Command("sources"))
async def cmd_sources(message: Message):
    async with aiosqlite.connect(DB_PATH) as db:
        cursor = await db.execute(
            "SELECT id, name, url, type, is_active FROM sources ORDER BY id DESC LIMIT 20"
        )
        sources = await cursor.fetchall()

    if not sources:
        await message.answer("📭 Пока нет добавленных источников.\nИспользуй /add")
        return

    text = "📋 <b>Список источников:</b>\n\n"
    for src in sources:
        status = "✅ Активен" if src[4] else "❌ Выключен"
        text += f"<b>{src[1]}</b> ({src[3]})\n{status}\n{src[2]}\n\n"

    await message.answer(text, parse_mode="HTML")

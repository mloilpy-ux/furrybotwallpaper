from aiogram import Router
from aiogram.types import Message
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
import aiosqlite

from database.db import DB_PATH
from config import ADMIN_ID

router = Router()

class AddSource(StatesGroup):
    waiting_for_url = State()

def is_admin(user_id: int) -> bool:
    return user_id == ADMIN_ID

@router.message(Command("add"))
async def cmd_add(message: Message, state: FSMContext):
    if not is_admin(message.from_user.id):
        await message.answer("⛔ Только админ может добавлять источники")
        return
    await message.answer(
        "Отправь ссылку на источник.\n\n"
        "Поддерживаются:\n"
        "• Reddit (https://www.reddit.com/r/название/)\n"
        "• Telegram (https://t.me/название)"
    )
    await state.set_state(AddSource.waiting_for_url)

@router.message(AddSource.waiting_for_url)
async def process_source_url(message: Message, state: FSMContext):
    if not is_admin(message.from_user.id):
        await state.clear()
        return
    url = message.text.strip()
    source_type = None
    if "reddit.com" in url:
        source_type = "reddit"
    elif "t.me" in url or url.startswith("@"):
        source_type = "telegram"
    else:
        await message.answer("❌ Неподдерживаемый тип источника.")
        await state.clear()
        return
    try:
        name = url.rstrip("/").split("/")[-1].replace("@", "")
        async with aiosqlite.connect(DB_PATH) as db:
            await db.execute(
                "INSERT INTO sources (name, url, type, added_by) VALUES (?, ?, ?, ?)",
                (name or url, url, source_type, message.from_user.id)
            )
            await db.commit()
        await message.answer(f"✅ Источник добавлен!\nТип: {source_type}")
    except Exception as e:
        await message.answer(f"❌ Ошибка: {e}")
    await state.clear()
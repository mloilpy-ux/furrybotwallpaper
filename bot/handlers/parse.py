from aiogram import Router
from aiogram.types import Message
from aiogram.filters import Command
from services.parser import parse_and_save_sources
from config import ADMIN_ID

router = Router()

@router.message(Command("parse"))
async def cmd_parse(message: Message):
    if message.from_user.id != ADMIN_ID:
        await message.answer("⛔ Только администратор")
        return
    
    await message.answer("🔄 Запускаю парсинг всех источников...")
    new_items = await parse_and_save_sources()
    await message.answer(f"✅ Парсинг завершён!\nДобавлено новых медиа: **{new_items}**", parse_mode="Markdown")

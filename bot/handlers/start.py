from aiogram import Router
from aiogram.types import Message
from aiogram.filters import Command

router = Router()

@router.message(Command("start"))
async def cmd_start(message: Message):
    text = (
        "🐾 <b>Furry Hub Bot</b>\n\n"
        "Привет! Я помогаю находить фурри-контент из разных источников.\n\n"
        "<b>Доступные команды:</b>\n"
        "/random — случайное изображение\n"
        "/sources — список источников\n"
        "/help — помощь"
    )
    await message.answer(text)

@router.message(Command("help"))
async def cmd_help(message: Message):
    await cmd_start(message)
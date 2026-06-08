from aiogram import Router, F
from aiogram.types import Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.filters import Command
import aiosqlite
import random

from database.db import DB_PATH

router = Router()

def get_keyboard():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="➡️ Следующее", callback_data="next_random")]
    ])

@router.message(Command("random"))
async def cmd_random(message: Message):
    await send_random(message)

@router.callback_query(F.data == "next_random")
async def next_random(callback: CallbackQuery):
    await send_random(callback.message)
    await callback.answer()

async def send_random(message: Message):
    async with aiosqlite.connect(DB_PATH) as db:
        # Показываем только SFW
        cursor = await db.execute(
            "SELECT media_url, title, post_url, is_gif FROM content WHERE is_nsfw=0 ORDER BY RANDOM() LIMIT 1"
        )
        result = await cursor.fetchone()

    if not result:
        await message.answer(
            "😕 Пока нет контента.\n"
            "Добавь источники через /add"
        )
        return

    media_url, title, post_url, is_gif = result

    caption = f"<b>{title or 'Без названия'}</b>"
    if post_url:
        caption += f"\n🔗 <a href=\"{post_url}\">Источник</a>"

    try:
        if is_gif or media_url.endswith(('.mp4', '.webm', '.gif')):
            await message.answer_video(media_url, caption=caption, reply_markup=get_keyboard())
        else:
            await message.answer_photo(media_url, caption=caption, reply_markup=get_keyboard())
    except Exception as e:
        # если не удалось отправить - пробуем как документ
        try:
            await message.answer_document(media_url, caption=caption, reply_markup=get_keyboard())
        except:
            await message.answer(f"❌ Ошибка: {e}\n{media_url}")
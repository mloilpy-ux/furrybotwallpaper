from aiogram import Router, F
from aiogram.types import Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.filters import Command
import aiosqlite
from database.db import DB_PATH
from config import ADMIN_ID

router = Router()

# Клавиатура
def get_random_kb():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="➡️ Следующее", callback_data="next")],
        [InlineKeyboardButton(text="❤️ Сохранить", callback_data="save")],
    ])

async def send_random(message: Message, nsfw: bool = False):
    async with aiosqlite.connect(DB_PATH) as db:
        query = """
            SELECT media_url, title, is_gif 
            FROM content 
            WHERE is_nsfw = ? 
            ORDER BY RANDOM() LIMIT 1
        """
        cur = await db.execute(query, (1 if nsfw else 0,))
        r = await cur.fetchone()
    
    if not r:
        await message.answer("❌ В базе пока нет подходящего контента.")
        return
    
    url, title, is_gif = r
    kb = get_random_kb()
    
    try:
        if url.endswith(('.mp4', '.gif')) or is_gif:
            await message.answer_video(url, caption=title[:200], reply_markup=kb)
        else:
            await message.answer_photo(url, caption=title[:200], reply_markup=kb)
    except Exception:
        # fallback
        try:
            await message.answer_document(url, caption=title[:200], reply_markup=kb)
        except Exception as e:
            await message.answer(f"❌ Не удалось отправить медиа: {e}")


@router.message(Command("random"))
async def cmd_random(m: Message):
    await send_random(m, nsfw=False)


@router.message(Command("random_nsfw"))
async def cmd_random_nsfw(m: Message):
    if m.from_user.id != ADMIN_ID:
        await m.answer("⛔ Только администратор")
        return
    await send_random(m, nsfw=True)


@router.callback_query(F.data == "next")
async def next_callback(c: CallbackQuery):
    await send_random(c.message)
    await c.answer("Следующее изображение 👀")


@router.callback_query(F.data == "save")
async def save_callback(c: CallbackQuery):
    # Пока заглушка — можно доработать под избранное позже
    await c.answer("❤️ Сохранено (пока в разработке)")

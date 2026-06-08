from aiogram import Router, F
from aiogram.types import Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.filters import Command
import aiosqlite
from database.db import DB_PATH

router = Router()
kb = InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text="➡️ Следующее", callback_data="next")],[InlineKeyboardButton(text="❤️ Сохранить", callback_data="save")]])

async def send_random(m):
    async with aiosqlite.connect(DB_PATH) as db:
        cur = await db.execute("SELECT media_url,title FROM content WHERE is_nsfw=0 ORDER BY RANDOM() LIMIT 1")
        r = await cur.fetchone()
    if not r: await m.answer("Нет контента"); return
    url, title = r
    try:
        if url.endswith(".mp4"): await m.answer_video(url, caption=title, reply_markup=kb)
        else: await m.answer_photo(url, caption=title, reply_markup=kb)
    except: await m.answer_document(url, caption=title, reply_markup=kb)

@router.message(Command("random"))
async def cmd(m: Message): await send_random(m)

@router.callback_query(F.data=="next")
async def nxt(c: CallbackQuery): await send_random(c.message); await c.answer()

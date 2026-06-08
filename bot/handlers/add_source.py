from aiogram import Router
from aiogram.types import Message
from aiogram.filters import Command
import aiosqlite
import re
from database.db import DB_PATH
from config import ADMIN_ID

router = Router()

def is_admin(uid: int) -> bool:
    return uid == ADMIN_ID

def detect_source(url: str):
    url = url.strip().lower()
    
    # Reddit
    if "reddit.com/r/" in url:
        match = re.search(r"reddit\.com/r/([^/]+)", url)
        if match:
            return "reddit", match.group(1), f"https://www.reddit.com/r/{match.group(1)}/"
    
    # Telegram
    if "t.me/" in url or url.startswith("@"):
        name = url.split("/")[-1].replace("@", "").split("?")[0]
        if name:
            return "telegram", name, f"https://t.me/{name}"
    
    # Twitter/X
    if "twitter.com/" in url or "x.com/" in url:
        match = re.search(r"(?:twitter|x)\.com/([^/?]+)", url)
        if match and match.group(1) not in ["home", "explore", "notifications"]:
            return "twitter", match.group(1), f"https://x.com/{match.group(1)}"
    
    return None, None, None

@router.message(Command("add"))
async def cmd_add(message: Message):
    if not is_admin(message.from_user.id):
        await message.answer("⛔ Только для админа")
        return
    
    args = message.text.split(maxsplit=1)
    if len(args) < 2:
        await message.answer(
            "📝 <b>Добавление источника</b>\n\n"
            "Использование:\n"
            "<code>/add https://www.reddit.com/r/furry</code>\n"
            "<code>/add https://t.me/furry_art</code>\n"
            "<code>/add https://x.com/FurryArt</code>\n"
            "<code>/add @furry_art</code>",
            parse_mode="HTML"
        )
        return
    
    url = args[1]
    source_type, name, clean_url = detect_source(url)
    
    if not source_type:
        await message.answer("❌ Неподдерживаемая ссылка\n\nПоддерживаются:\n• Reddit\n• Telegram\n• Twitter/X")
        return
    
    try:
        async with aiosqlite.connect(DB_PATH) as db:
            await db.execute(
                "INSERT OR IGNORE INTO sources (name, url, type, added_by, is_active) VALUES (?, ?, ?, ?, 1)",
                (name, clean_url, source_type, message.from_user.id)
            )
            await db.commit()
        
        emoji = {"reddit": "🟠", "telegram": "✈️", "twitter": "🐦"}
        await message.answer(
            f"{emoji.get(source_type, '✅')} <b>Источник добавлен!</b>\n\n"
            f"Тип: {source_type}\n"
            f"Имя: {name}\n"
            f"URL: {clean_url}\n\n"
            f"Теперь запусти /parse",
            parse_mode="HTML"
        )
        
    except Exception as e:
        await message.answer(f"❌ Ошибка базы данных: {e}")

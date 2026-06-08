import asyncio
import logging
from aiogram import Bot, Dispatcher
from aiogram.enums import ParseMode
from aiogram.client.default import DefaultBotProperties

from config import BOT_TOKEN
from database.db import init_db
from handlers.start import router as start_router
from handlers.add_source import router as add_router
from handlers.sources import router as sources_router
from handlers.random import router as random_router
from handlers.parse import router as parse_router
from services.parser import parse_and_save_sources

logging.basicConfig(level=logging.INFO)

async def main():
    await init_db()

    # Автоматический парсинг при запуске
    print("🔄 Запускаем парсинг источников...")
    try:
        await parse_and_save_sources()
    except Exception as e:
        logging.error(f"Ошибка при стартовом парсинге: {e}")

    bot = Bot(
        token=BOT_TOKEN,
        default=DefaultBotProperties(parse_mode=ParseMode.HTML)
    )
    dp = Dispatcher()

    dp.include_router(start_router)
    dp.include_router(add_router)
    dp.include_router(sources_router)
    dp.include_router(random_router)
    dp.include_router(parse_router)

    print("✅ Бот успешно запущен")
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
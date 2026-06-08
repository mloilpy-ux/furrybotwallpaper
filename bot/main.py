import asyncio
import logging
from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode

from config import BOT_TOKEN
from database.db import init_db
from services.parser import parse_and_save_sources

# Импорт роутеров
from bot.handlers.random import router as random_router
from bot.handlers.add_source import router as add_router
from bot.handlers.sources import router as sources_router
from bot.handlers.parse import router as parse_router

# Настройка логирования
logging.basicConfig(level=logging.INFO)

async def main():
    # Инициализация БД
    await init_db()
    
    # Инициализация бота
    bot = Bot(
        token=BOT_TOKEN,
        default=DefaultBotProperties(parse_mode=ParseMode.HTML)
    )
    
    dp = Dispatcher()
    
    # Регистрация роутеров
    dp.include_router(random_router)
    dp.include_router(add_router)
    dp.include_router(sources_router)
    dp.include_router(parse_router)
    
    # Автопарсинг при старте
    asyncio.create_task(parse_and_save_sources())
    
    print("🤖 Бот запущен! Furry Wallpaper Bot")
    
    # Запуск polling
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())

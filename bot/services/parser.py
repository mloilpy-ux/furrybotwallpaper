import aiosqlite
from services.reddit import parse_reddit
from services.twitter import parse_twitter
# ...
elif stype == "twitter":
    items = await parse_twitter(url)
from services.telegram import parse_telegram
from database.db import DB_PATH

async def parse_and_save_sources():
    """Парсит все активные источники и сохраняет контент"""
    async with aiosqlite.connect(DB_PATH) as db:
        cursor = await db.execute(
            "SELECT id, url, type FROM sources WHERE is_active = 1"
        )
        sources = await cursor.fetchall()

    total_added = 0

    for source_id, url, source_type in sources:
        items = []

        if source_type == "reddit":
            items = await parse_reddit(url)
        elif source_type == "telegram":
            items = await parse_telegram(url)
        # twitter пропускаем - без API не вариант

        if not items:
            continue

        # Батчевая вставка - одно соединение
        try:
            async with aiosqlite.connect(DB_PATH) as db:
                for item in items:
                    try:
                        cursor = await db.execute(
                            """INSERT OR IGNORE INTO content 
                               (source_id, title, media_url, post_url, is_nsfw, is_gif)
                               VALUES (?, ?, ?, ?, ?, ?)""",
                            (source_id, item["title"][:300], item["media_url"], 
                             item["post_url"], int(item["is_nsfw"]), int(item["is_gif"]))
                        )
                        if cursor.rowcount > 0:
                            total_added += 1
                    except:
                        pass
                await db.commit()
        except Exception as e:
            print(f"Ошибка сохранения {url}: {e}")

    print(f"Парсинг завершён. Добавлено {total_added} элементов.")
    return total_added

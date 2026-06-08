import aiosqlite
from typing import List
from database.db import DB_PATH

# Импорты парсеров
try:
    from services.reddit import parse_reddit
except ImportError:
    async def parse_reddit(url, limit=20): return []

try:
    from services.telegram import parse_telegram
except ImportError:
    async def parse_telegram(url, limit=20): return []

try:
    from services.twitter import parse_twitter
except ImportError:
    async def parse_twitter(url, limit=20): return []


async def parse_and_save_sources() -> int:
    """
    Парсит все активные источники и сохраняет в БД
    Возвращает количество добавленных элементов
    """
    print("[PARSER] Starting parse...")
    
    # Получаем источники
    async with aiosqlite.connect(DB_PATH) as db:
        cursor = await db.execute(
            "SELECT id, url, type, name FROM sources WHERE is_active = 1"
        )
        sources = await cursor.fetchall()
    
    if not sources:
        print("[PARSER] No active sources found")
        return 0
    
    print(f"[PARSER] Found {len(sources)} sources")
    total_added = 0
    
    for source_id, url, source_type, name in sources:
        print(f"[PARSER] Processing {source_type}: {name}")
        
        items = []
        try:
            if source_type == "reddit":
                items = await parse_reddit(url, limit=25)
            elif source_type == "telegram":
                items = await parse_telegram(url, limit=20)
            elif source_type == "twitter":
                items = await parse_twitter(url, limit=20)
            else:
                print(f"[PARSER] Unknown type: {source_type}")
                continue
        except Exception as e:
            print(f"[PARSER] Error parsing {url}: {e}")
            continue
        
        print(f"[PARSER] Got {len(items)} items from {name}")
        
        # Сохраняем в БД
        if items:
            try:
                async with aiosqlite.connect(DB_PATH) as db:
                    for item in items:
                        try:
                            cursor = await db.execute(
                                """INSERT OR IGNORE INTO content 
                                   (source_id, title, media_url, post_url, is_nsfw, is_gif)
                                   VALUES (?, ?, ?, ?, ?, ?)""",
                                (
                                    source_id,
                                    item.get("title", "")[:300],
                                    item.get("media_url", ""),
                                    item.get("post_url", ""),
                                    int(item.get("is_nsfw", False)),
                                    int(item.get("is_gif", False))
                                )
                            )
                            if cursor.rowcount > 0:
                                total_added += 1
                        except Exception as e:
                            print(f"[PARSER] DB insert error: {e}")
                            continue
                    
                    await db.commit()
            except Exception as e:
                print(f"[PARSER] DB error: {e}")
    
    print(f"[PARSER] Completed. Total new items: {total_added}")
    return total_added

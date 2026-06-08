import aiohttp
import os
import asyncio
from typing import List, Dict
from database.db import DB_PATH
import aiosqlite

SCRAPEOPS_KEY = os.getenv("SCRAPEOPS_KEY", "")

async def parse_reddit(url: str, limit: int = 30) -> List[Dict]:
    """Парсинг Reddit (subreddit)"""
    try:
        sub = url.split("/r/")[1].split("/")[0].strip()
        target = f"https://api.reddit.com/r/{sub}/hot?limit={limit}"
        
        proxy = f"https://proxy.scrapeops.io/v1/?api_key={SCRAPEOPS_KEY}&url={target}" if SCRAPEOPS_KEY else target
        
        headers = {"User-Agent": "FurryBotWallpaper/1.0"}
        
        async with aiohttp.ClientSession() as session:
            async with session.get(proxy, headers=headers, timeout=25) as resp:
                if resp.status != 200:
                    print(f"[REDDIT] Ошибка {resp.status} для {sub}")
                    return []
                
                data = await resp.json()
                posts = data.get("data", {}).get("children", [])
                
                items = []
                for post in posts:
                    d = post.get("data", {})
                    media_url = d.get("url_overridden_by_dest") or d.get("url", "")
                    
                    if any(ext in media_url.lower() for ext in (".jpg", ".png", ".jpeg", ".gif")):
                        items.append({
                            "title": d.get("title", "")[:250],
                            "media_url": media_url,
                            "post_url": f"https://reddit.com{d.get('permalink', '')}",
                            "is_nsfw": bool(d.get("over_18", False)),
                            "is_gif": media_url.lower().endswith(".gif")
                        })
                print(f"[REDDIT] {sub} → найдено {len(items)} изображений")
                return items
                
    except Exception as e:
        print(f"[REDDIT] Критическая ошибка: {e}")
        return []


async def parse_telegram(url: str, limit: int = 20) -> List[Dict]:
    """Парсинг публичных Telegram-каналов через t.me/s/"""
    try:
        channel = url.split("t.me/")[-1].split("/")[0].strip()
        target = f"https://t.me/s/{channel}"
        
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
        }
        
        async with aiohttp.ClientSession() as session:
            async with session.get(target, headers=headers, timeout=20) as resp:
                if resp.status != 200:
                    print(f"[TELEGRAM] Ошибка {resp.status} для {channel}")
                    return []
                
                text = await resp.text()
                
                # Простой, но надёжный поиск медиа
                items = []
                import re
                # Ищем ссылки на изображения
                img_matches = re.findall(r'href="(/[^"]+)"[^>]*class="[^"]*tgme_widget_message_photo[^"]*"', text)
                
                for match in img_matches[:limit]:
                    full_url = f"https://t.me{match}"
                    items.append({
                        "title": f"Пост из @{channel}",
                        "media_url": full_url,
                        "post_url": full_url,
                        "is_nsfw": False,  # Telegram-каналы обычно имеют свою маркировку
                        "is_gif": False
                    })
                
                print(f"[TELEGRAM] @{channel} → найдено {len(items)} медиа")
                return items
                
    except Exception as e:
        print(f"[TELEGRAM] Ошибка: {e}")
        return []


async def parse_and_save_sources():
    """Основная функция парсинга всех источников"""
    print("🔄 [PARSER] Запуск парсинга источников...")
    
    async with aiosqlite.connect(DB_PATH) as db:
        async with db.execute(
            "SELECT id, name, url, type FROM sources WHERE is_active = 1"
        ) as cursor:
            sources = await cursor.fetchall()
    
    if not sources:
        print("⚠️ Нет активных источников. Добавьте через /add")
        return 0
    
    total_new = 0
    for sid, name, url, stype in sources:
        print(f"📡 Парсинг {stype}: {name}")
        
        if stype == "reddit":
            items = await parse_reddit(url)
        elif stype == "telegram":
            items = await parse_telegram(url)
        else:
            print(f"❌ Неизвестный тип: {stype}")
            continue
        
        if not items:
            continue
            
        async with aiosqlite.connect(DB_PATH) as db:
            for item in items:
                try:
                    cursor = await db.execute("""
                        INSERT OR IGNORE INTO content 
                        (source_id, title, media_url, post_url, is_nsfw, is_gif)
                        VALUES (?, ?, ?, ?, ?, ?)
                    """, (
                        sid, 
                        item["title"], 
                        item["media_url"], 
                        item["post_url"], 
                        int(item["is_nsfw"]), 
                        int(item["is_gif"])
                    ))
                    if cursor.rowcount > 0:
                        total_new += 1
                except Exception as e:
                    print(f"Ошибка сохранения: {e}")
            await db.commit()
    
    print(f"✅ [PARSER] Завершено. Добавлено новых: {total_new}")
    return total_new

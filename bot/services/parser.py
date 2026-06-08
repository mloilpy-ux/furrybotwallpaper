import aiosqlite
from database.db import DB_PATH
from services.reddit import parse_reddit
from services.telegram import parse_telegram
from services.twitter import parse_twitter

async def parse_and_save_sources():
    async with aiosqlite.connect(DB_PATH) as db:
        cur = await db.execute("SELECT id, url, type FROM sources WHERE is_active=1")
        sources = await cur.fetchall()
    
    total = 0
    for sid, url, stype in sources:
        items = []
        if stype == "reddit":
            items = await parse_reddit(url)
        elif stype == "telegram":
            items = await parse_telegram(url)
        elif stype == "twitter":
            items = await parse_twitter(url)
        
        if items:
            async with aiosqlite.connect(DB_PATH) as db:
                for it in items:
                    cur = await db.execute(
                        "INSERT OR IGNORE INTO content (source_id, title, media_url, post_url, is_nsfw, is_gif) VALUES (?,?,?,?,?,?)",
                        (sid, it["title"], it["media_url"], it["post_url"], int(it["is_nsfw"]), int(it["is_gif"]))
                    )
                    if cur.rowcount > 0:
                        total += 1
                await db.commit()
    return total

import aiosqlite
from database.db import DB_PATH
from services.reddit import parse_reddit

async def parse_and_save_sources():
    print("[PARSER] Starting")
    async with aiosqlite.connect(DB_PATH) as db:
        cur = await db.execute("SELECT id, url, type, name FROM sources WHERE is_active=1")
        sources = await cur.fetchall()
    
    print(f"[PARSER] Sources: {len(sources)}")
    total = 0
    
    for sid, url, stype, name in sources:
        print(f"[PARSER] Parsing {name} ({stype})")
        items = []
        
        if stype == "reddit":
            items = await parse_reddit(url)
        elif stype == "telegram":
            try:
                from services.telegram import parse_telegram
                items = await parse_telegram(url)
            except:
                items = []
        elif stype == "twitter":
            try:
                from services.twitter import parse_twitter
                items = await parse_twitter(url)
            except:
                items = []
        
        print(f"[PARSER] Got {len(items)} items")
        
        if items:
            async with aiosqlite.connect(DB_PATH) as db:
                for it in items:
                    try:
                        cur = await db.execute(
                            "INSERT OR IGNORE INTO content (source_id, title, media_url, post_url, is_nsfw, is_gif) VALUES (?,?,?,?,?,?)",
                            (sid, it["title"], it["media_url"], it["post_url"], int(it["is_nsfw"]), int(it["is_gif"]))
                        )
                        if cur.rowcount > 0:
                            total += 1
                    except Exception as e:
                        print(f"[DB] {e}")
                await db.commit()
    
    print(f"[PARSER] Done. Added: {total}")
    return total

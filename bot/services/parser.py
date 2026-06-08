import aiosqlite
import aiohttp
import os
from database.db import DB_PATH

SCRAPEOPS_KEY = os.getenv("SCRAPEOPS_KEY", "")

async def parse_reddit(url: str, limit: int = 25):
    try:
        sub = url.split("/r/")[1].split("/")[0]
        target = f"https://api.reddit.com/r/{sub}/hot?limit={limit}"
        proxy = f"https://proxy.scrapeops.io/v1/?api_key={SCRAPEOPS_KEY}&url={target}" if SCRAPEOPS_KEY else target
        
        print(f"[REDDIT] Fetching {sub}")
        async with aiohttp.ClientSession() as s:
            async with s.get(proxy, headers={"User-Agent":"Mozilla/5.0"}, timeout=20) as r:
                print(f"[REDDIT] Status {r.status}")
                if r.status != 200:
                    txt = await r.text()
                    print(f"[REDDIT] Error: {txt[:100]}")
                    return []
                data = await r.json()
                posts = data.get("data", {}).get("children", [])
                print(f"[REDDIT] Posts in JSON: {len(posts)}")
                
                out = []
                for p in posts:
                    d = p["data"]
                    u = d.get("url_overridden_by_dest") or d.get("url", "")
                    if ".jpg" in u or ".png" in u or ".jpeg" in u:
                        out.append({
                            "title": d.get("title", "")[:200],
                            "media_url": u,
                            "post_url": f"https://reddit.com{d.get('permalink','')}",
                            "is_nsfw": d.get("over_18", False),
                            "is_gif": False
                        })
                print(f"[REDDIT] Filtered images: {len(out)}")
                return out
    except Exception as e:
        print(f"[REDDIT] Exception: {e}")
        import traceback; traceback.print_exc()
        return []

async def parse_and_save_sources():
    print("[PARSER] === START ===")
    async with aiosqlite.connect(DB_PATH) as db:
        cur = await db.execute("SELECT id, url, type, name FROM sources WHERE is_active=1")
        sources = await cur.fetchall()
    
    print(f"[PARSER] Active sources: {len(sources)}")
    for s in sources:
        print(f"[PARSER] - {s[2]}: {s[3]} ({s[1]})")
    
    if not sources:
        print("[PARSER] NO SOURCES - add with /add")
        return 0
    
    total = 0
    for sid, url, stype, name in sources:
        items = []
        if stype == "reddit":
            items = await parse_reddit(url)
        print(f"[PARSER] {name} -> {len(items)} items")
        
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
    
    print(f"[PARSER] === DONE: {total} new ===")
    return total

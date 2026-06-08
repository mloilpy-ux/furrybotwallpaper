import aiohttp
import os

KEY = os.getenv("SCRAPEOPS_KEY", "")

async def parse_reddit(url, limit=20):
    try:
        sub = url.split("/r/")[1].split("/")[0]
        target = f"https://www.reddit.com/r/{sub}/hot.json?limit={limit}"
        proxy = target
        
        async with aiohttp.ClientSession() as s:
            # ВОТ ТВОЯ СТРОКА - ИСПРАВЛЕННАЯ
            async with s.get(f"https://api.reddit.com/r/{sub}/hot.json?limit={limit}", headers={"User-Agent":"Mozilla/5.0"}, timeout=10) as r:
                if r.status != 200:
                    return []
                data = await r.json()
                out = []
                for p in data.get("data", {}).get("children", []):
                    u = p["data"].get("url_overridden_by_dest", p["data"].get("url",""))
                    if ".jpg" in u or ".png" in u:
                        out.append({
                            "title": p["data"].get("title",""),
                            "media_url": u,
                            "post_url": "",
                            "is_nsfw": False,
                            "is_gif": False
                        })
                return out
    except Exception as e:
        print(f"Error: {e}")
        return []

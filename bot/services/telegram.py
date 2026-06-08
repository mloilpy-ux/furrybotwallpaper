import aiohttp
import re
from typing import List, Dict

async def parse_telegram(url: str, limit: int = 20) -> List[Dict]:
    try:
        channel = url.split("/")[-1].replace("@", "")
        async with aiohttp.ClientSession() as s:
            async with s.get(f"https://t.me/s/{channel}", headers={"User-Agent": "Mozilla/5.0"}, timeout=10) as r:
                html = await r.text()
        imgs = re.findall(r"background-image:url\('([^']+)'\)", html)
        return [{"title": "", "media_url": i, "post_url": url, "is_nsfw": False, "is_gif": False} for i in imgs[:limit]]
    except:
        return []

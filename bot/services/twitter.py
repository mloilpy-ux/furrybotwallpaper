import aiohttp
import re
from typing import List, Dict

async def parse_twitter(url: str, limit: int = 20) -> List[Dict]:
    try:
        user = url.split("/")[-1].split("?")[0]
        async with aiohttp.ClientSession() as s:
            async with s.get(f"https://nitter.net/{user}/rss", timeout=10) as r:
                txt = await r.text()
        imgs = re.findall(r'https://pbs\.twimg\.com/media/[^"<\s]+', txt)
        return [{"title": "", "media_url": i, "post_url": url, "is_nsfw": False, "is_gif": False} for i in imgs[:limit]]
    except:
        return []

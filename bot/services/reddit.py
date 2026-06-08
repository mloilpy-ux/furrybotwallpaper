import aiohttp
import os
from typing import List, Dict

SCRAPEOPS_KEY = os.getenv("SCRAPEOPS_KEY", "")

async def parse_reddit(url: str, limit: int = 25) -> List[Dict]:
    try:
        subreddit = url.split("/r/")[1].split("/")[0].strip()
        target = f"https://api.reddit.com/r/{subreddit}/hot?limit={limit}&raw_json=1"
        
        if SCRAPEOPS_KEY:
            proxy = f"https://proxy.scrapeops.io/v1/?api_key={SCRAPEOPS_KEY}&url={target}"
        else:
            proxy = target
        
        async with aiohttp.ClientSession() as s:
            async with s.get(proxy, headers={"User-Agent": "Mozilla/5.0"}, timeout=15) as r:
                if r.status != 200:
                    return []
                data = await r.json()
                out = []
                for p in data.get("data", {}).get("children", []):
                    d = p.get("data", {})
                    u = d.get("url_overridden_by_dest") or d.get("url", "")
                    if any(x in u.lower() for x in [".jpg", ".jpeg", ".png", ".gif", ".webp"]):
                        out.append({
                            "title": d.get("title", "")[:300],
                            "media_url": u,
                            "post_url": f"https://reddit.com{d.get('permalink','')}",
                            "is_nsfw": d.get("over_18", False),
                            "is_gif": u.lower().endswith(".gif")
                        })
                return out
    except Exception:
        return []

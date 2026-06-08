import aiohttp
import os

KEY = os.getenv("SCRAPEOPS_KEY", "")

async def parse_reddit(url, limit=25):
    # Обычная ссылка https://www.reddit.com/r/furry/
    try:
        sub = url.split("/r/")[1].split("/")[0]
    except:
        return []
    
    target = f"https://www.reddit.com/r/{sub}/hot.json?limit={limit}"
    
    # Прокси
    fetch_url = f"https://proxy.scrapeops.io/v1/?api_key={KEY}&url={target}" if KEY else target
    
    try:
        async with aiohttp.ClientSession() as s:
            async with s.get(fetch_url, headers={"User-Agent":"Mozilla/5.0"}, timeout=20) as r:
                if r.status != 200:
                    return []
                j = await r.json()
                out = []
                for p in j.get("data",{}).get("children",[]):
                    d = p["data"]
                    u = d.get("url_overridden_by_dest") or d.get("url","")
                    if ".jpg" in u or ".png" in u or ".jpeg" in u:
                        out.append({
                            "title": d.get("title","")[:200],
                            "media_url": u,
                            "post_url": "https://reddit.com"+d.get("permalink",""),
                            "is_nsfw": bool(d.get("over_18")),
                            "is_gif": u.endswith(".gif")
                        })
                return out
    except:
        return []

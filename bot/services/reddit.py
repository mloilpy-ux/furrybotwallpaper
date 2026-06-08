import aiohttp
import os
from typing import List, Dict

SCRAPEOPS_KEY = os.getenv("SCRAPEOPS_KEY", "")

async def parse_reddit(url: str, limit: int = 25) -> List[Dict]:
    """Reddit через ScrapeOps Proxy API"""
    try:
        # Извлекаем сабреддит
        if "/r/" not in url:
            return []
        subreddit = url.split("/r/")[1].split("/")[0].strip()
        
        # Целевой URL
        target_url = f"https://old.reddit.com/r/{subreddit}/hot.json?limit={limit}&raw_json=1"
        
        # Прокси
        if SCRAPEOPS_KEY:
            proxy_url = f"https://proxy.scrapeops.io/v1/?api_key={SCRAPEOPS_KEY}&url={target_url}&country=us"
        else:
            proxy_url = target_url
        
        headers = {"User-Agent": "Mozilla/5.0"}
        
        async with aiohttp.ClientSession() as session:
            async with session.get(proxy_url, headers=headers, timeout=20) as resp:
                if resp.status != 200:
                    print(f"[REDDIT] HTTP {resp.status}")
                    return []
                
                data = await resp.json()
                posts = data.get("data", {}).get("children", [])
                
                results = []
                for post in posts:
                    pd = post.get("data", {})
                    media_url = pd.get("url_overridden_by_dest") or pd.get("url", "")
                    
                    # Фильтр медиа
                    if not media_url:
                        continue
                    
                    # Пропускаем текст
                    if any(x in media_url for x in ["reddit.com", "/comments/", "v.redd.it", "youtu"]):
                        # Пробуем preview
                        preview = pd.get("preview", {}).get("images", [])
                        if preview:
                            media_url = preview[0]["source"]["url"].replace("&amp;", "&")
                        else:
                            continue
                    
                    # Только изображения
                    if not any(ext in media_url.lower() for ext in [".jpg", ".jpeg", ".png", ".gif", ".webp"]):
                        continue
                    
                    results.append({
                        "title": pd.get("title", "")[:300],
                        "media_url": media_url,
                        "post_url": f"https://reddit.com{pd.get('permalink', '')}",
                        "is_nsfw": pd.get("over_18", False),
                        "is_gif": media_url.lower().endswith((".gif", ".gifv"))
                    })
                
                print(f"[REDDIT] Parsed {len(results)} from r/{subreddit}")
                return results
                
    except Exception as e:
        print(f"[REDDIT] Error: {e}")
        return []

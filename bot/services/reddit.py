import aiohttp
import os
from typing import List, Dict

SCRAPEOPS_KEY = os.getenv("SCRAPEOPS_KEY", "")

async def parse_reddit(url: str, limit: int = 25) -> List[Dict]:
    try:
        subreddit = url.split("/r/")[1].split("/")[0].strip()
        
        # Используем api.reddit.com - работает лучше всего
        target_url = f"https://api.reddit.com/r/{subreddit}/hot?limit={limit}&raw_json=1"
        
        # Через ScrapeOps если есть ключ
        if SCRAPEOPS_KEY:
            proxy_url = f"https://proxy.scrapeops.io/v1/?api_key={SCRAPEOPS_KEY}&url={target_url}"
        else:
            proxy_url = target_url
        
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
        }
        
        async with aiohttp.ClientSession() as session:
            async with session.get(proxy_url, headers=headers, timeout=20) as resp:
                print(f"[REDDIT] {subreddit} status: {resp.status}")
                
                if resp.status != 200:
                    text = await resp.text()
                    print(f"[REDDIT] Error body: {text[:200]}")
                    return []
                
                data = await resp.json()
                print(f"[REDDIT] JSON keys: {data.keys()}")
                print(f"[REDDIT] Posts count: {len(data.get('data',{}).get('children',[]))}")
                if posts:
                print(f"[REDDIT] First post url: {posts[0]['data'].get('url')}")
                posts = data.get("data", {}).get("children", [])
                  
                results = []
                for post in posts:
                    pd = post.get("data", {})
                    media_url = pd.get("url_overridden_by_dest") or pd.get("url", "")
                    
                    if not media_url:
                        continue
                    
                    # Фильтруем
                    if "reddit.com" in media_url and "/comments/" in media_url:
                        continue
                    
                    if not any(ext in media_url.lower() for ext in [".jpg", ".jpeg", ".png", ".gif", ".webp"]):
                        # Пробуем preview
                        preview = pd.get("preview", {}).get("images", [])
                        if preview:
                            media_url = preview[0]["source"]["url"].replace("&amp;", "&")
                        else:
                            continue
                    
                    results.append({
                        "title": pd.get("title", "")[:300],
                        "media_url": media_url,
                        "post_url": f"https://reddit.com{pd.get('permalink', '')}",
                        "is_nsfw": pd.get("over_18", False),
                        "is_gif": media_url.lower().endswith((".gif", ".mp4"))
                    })
                
                print(f"[REDDIT] Success: {len(results)} items")
                return results
                
    except Exception as e:
        print(f"[REDDIT] Exception: {e}")
        import traceback
        traceback.print_exc()
        return []

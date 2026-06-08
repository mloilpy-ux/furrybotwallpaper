import aiohttp
from typing import List, Dict

# Рабочие инстансы Libreddit (меняй если один упадёт)
LIBREDDIT_INSTANCES = [
    "https://libreddit.spike.codes",
    "https://libreddit.kavin.rocks",
    "https://reddit.smnz.de",
    "https://libreddit.privacydev.net"
]

async def parse_reddit(url: str, limit: int = 25) -> List[Dict]:
    """Парсит Reddit через Libreddit без API"""
    try:
        # Извлекаем сабреддит
        if "/r/" not in url:
            return []
        
        subreddit = url.split("/r/")[1].split("/")[0].strip()
        
        # Пробуем разные инстансы
        for base in LIBREDDIT_INSTANCES:
            try:
                api_url = f"{base}/r/{subreddit}/hot.json?limit={limit}"
                
                headers = {
                    "User-Agent": "Mozilla/5.0 (compatible; FurryBot/1.0)"
                }
                
                async with aiohttp.ClientSession() as session:
                    async with session.get(api_url, headers=headers, timeout=15) as resp:
                        if resp.status != 200:
                            continue
                        
                        data = await resp.json()
                        posts = data.get("data", {}).get("children", [])
                        
                        results = []
                        for post in posts:
                            pd = post.get("data", {})
                            
                            # Берём прямую ссылку на медиа
                            media_url = pd.get("url_overridden_by_dest") or pd.get("url", "")
                            
                            # Фильтруем только картинки/гифки
                            if not any(media_url.lower().endswith(ext) for ext in (".jpg", ".jpeg", ".png", ".gif", ".webp")):
                                # Пробуем preview
                                preview = pd.get("preview", {}).get("images", [])
                                if preview:
                                    media_url = preview[0].get("source", {}).get("url", "").replace("&amp;", "&")
                                else:
                                    continue
                            
                            # Пропускаем видео и ссылки
                            if "v.redd.it" in media_url or "reddit.com" in media_url and "/comments/" in media_url:
                                continue
                            
                            results.append({
                                "title": pd.get("title", "")[:300],
                                "media_url": media_url,
                                "post_url": f"https://reddit.com{pd.get('permalink', '')}",
                                "is_nsfw": pd.get("over_18", False),
                                "is_gif": media_url.endswith((".gif", ".mp4"))
                            })
                        
                        if results:
                            print(f"[REDDIT] {subreddit}: {len(results)} posts via {base}")
                            return results
                            
            except Exception as e:
                print(f"[REDDIT] {base} failed: {e}")
                continue
        
        return []
        
    except Exception as e:
        print(f"[REDDIT] Fatal error: {e}")
        return []

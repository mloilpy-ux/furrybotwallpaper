import aiohttp
from typing import List, Dict

async def parse_reddit(url: str, limit: int = 25) -> List[Dict]:
    """Парсит Reddit без API - работает через public JSON"""
    if not url.endswith('/'):
        url += '/'
    
    # Пробуем old.reddit - меньше блокировок
    if "reddit.com" in url:
        url = url.replace("www.reddit.com", "old.reddit.com")
    
    api_url = f"{url}hot.json?limit={limit}"
    
    headers = {
        "User-Agent": "Mozilla/5.0 (compatible; FurryBot/1.0; +https://github.com)"
    }

    async with aiohttp.ClientSession() as session:
        try:
            async with session.get(api_url, headers=headers, timeout=20) as resp:
                if resp.status != 200:
                    print(f"Reddit {resp.status}")
                    return []
                
                data = await resp.json()
                posts = data.get("data", {}).get("children", [])
                
                results = []
                for post in posts:
                    pd = post.get("data", {})
                    media_url = pd.get("url_overridden_by_dest") or pd.get("url")
                    
                    if not media_url:
                        continue
                    
                    # Пропускаем текст и ссылки на реддит
                    if media_url.startswith("https://www.reddit.com") or "/comments/" in media_url:
                        # проверяем галерею
                        if pd.get("is_gallery"):
                            gallery = pd.get("media_metadata", {})
                            for item in gallery.values():
                                if "s" in item and "u" in item["s"]:
                                    img = item["s"]["u"].replace("&amp;", "&")
                                    results.append({
                                        "title": pd.get("title", ""),
                                        "media_url": img,
                                        "post_url": f"https://reddit.com{pd.get('permalink', '')}",
                                        "is_nsfw": pd.get("over_18", False),
                                        "is_gif": False
                                    })
                        continue
                    
                    # gifv -> mp4
                    if media_url.endswith('.gifv'):
                        media_url = media_url.replace('.gifv', '.mp4')
                    
                    # Фильтруем только медиа
                    if not any(media_url.lower().endswith(ext) for ext in ('.jpg','.jpeg','.png','.gif','.mp4','.webm')):
                        # пробуем preview
                        preview = pd.get("preview", {}).get("images", [])
                        if preview:
                            media_url = preview[0]["source"]["url"].replace("&amp;", "&")
                        else:
                            continue
                    
                    results.append({
                        "title": pd.get("title", ""),
                        "media_url": media_url,
                        "post_url": f"https://reddit.com{pd.get('permalink', '')}",
                        "is_nsfw": pd.get("over_18", False),
                        "is_gif": media_url.endswith(('.gif', '.mp4', '.webm'))
                    })
                
                return results
        except Exception as e:
            print(f"Reddit parse error: {e}")
            return []
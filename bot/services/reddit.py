import aiohttp

async def parse_reddit(url: str, limit: int = 20):
    # Используем прокси-инстанс
    if "reddit.com/r/" in url:
        sub = url.split("/r/")[1].strip("/")
        api = f"https://r.jina.ai/http://old.reddit.com/r/{sub}/hot.json?limit={limit}"
    else:
        return []
    
    headers = {"User-Agent": "Mozilla/5.0"}
    
    try:
        async with aiohttp.ClientSession() as s:
            async with s.get(api, headers=headers, timeout=20) as r:
                data = await r.json()
                posts = data.get("data", {}).get("children", [])
                out = []
                for p in posts:
                    d = p["data"]
                    u = d.get("url_overridden_by_dest", "")
                    if any(u.endswith(x) for x in (".jpg",".png",".jpeg",".gif")):
                        out.append({
                            "title": d.get("title",""),
                            "media_url": u,
                            "post_url": "https://reddit.com" + d.get("permalink",""),
                            "is_nsfw": d.get("over_18", False),
                            "is_gif": u.endswith(".gif")
                        })
                return out
    except Exception as e:
        print(f"Reddit error: {e}")
        return []

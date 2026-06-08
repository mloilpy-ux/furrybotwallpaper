import aiohttp
from bs4 import BeautifulSoup

async def parse_twitter(url, limit=20):
    user = url.split("/")[-1]
    api = f"https://nitter.net/{user}/rss"
    async with aiohttp.ClientSession() as s:
        async with s.get(api) as r:
            text = await r.text()
    # парсинг RSS, ищем картинки
    import re
    imgs = re.findall(r'https://pbs.twimg.com/media/[^\"]+\.(jpg|png)', text)
    return [{"title":"","media_url:i,"post_url":url,"is_nsfw":False,"is_gif":False} for i in imgs[:limit]]

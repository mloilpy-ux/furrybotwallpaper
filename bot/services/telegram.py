import aiohttp, re
async def parse_telegram(url, limit=20):
    ch = url.split("/")[-1].replace("@","")
    async with aiohttp.ClientSession() as s:
        async with s.get(f"https://t.me/s/{ch}", headers={"User-Agent":"Mozilla/5.0"}) as r:
            html = await r.text()
    imgs = re.findall(r"background-image:url\('([^']+)'\)", html)
    return [{"title":"","media_url":i,"post_url":url,"is_nsfw":False,"is_gif":False} for i in imgs[:limit]]

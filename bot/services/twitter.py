import aiohttp, re
async def parse_twitter(url: str, limit: int = 20):
    user = url.split("/")[-1].split("?")[0]
    for host in ["nitter.net","nitter.privacydev.net","nitter.it"]:
        try:
            api = f"https://{host}/{user}/rss"
            async with aiohttp.ClientSession() as s:
                async with s.get(api, timeout=10) as r:
                    txt = await r.text()
                    imgs = re.findall(r'<img src="(https://pbs.twimg.com/media/[^"]+)"', txt)
                    return [{"title":"","media_url":i+":large","post_url":url,"is_nsfw":False,"is_gif":False} for i in imgs[:limit]]
        except: continue
    return []

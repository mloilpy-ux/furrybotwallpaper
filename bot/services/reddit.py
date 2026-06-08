import aiohttp

async def parse_reddit(url: str, limit: int = 20):
    try:
        sub = url.split("/r/")[1].split("/")[0]
        # Используем 4 разных зеркала
        for host in ["libreddit.spike.codes","safereddit.com","reddit.smnz.de","libreddit.privacydev.net"]:
            try:
                api = f"https://{host}/r/{sub}/hot.json?raw_json=1"
                async with aiohttp.ClientSession() as s:
                    async with s.get(api, timeout=10, headers={"User-Agent":"curl/7.0"}) as r:
                        if r.status == 200:
                            j = await r.json()
                            out = []
                            for p in j["data"]["children"][:limit]:
                                d = p["data"]
                                u = d.get("url","")
                                if ".jpg" in u or ".png" in u:
                                    out.append({"title":d["title"],"media_url":u,"post_url":"https://reddit.com"+d["permalink"],"is_nsfw":d["over_18"],"is_gif":False})
                            if out: return out
            except: continue
    except: pass
    return []

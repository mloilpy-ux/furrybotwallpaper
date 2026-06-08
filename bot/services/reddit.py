import aiohttp
async def parse_reddit(url, limit=20):
    sub = url.split("/r/")[1].split("/")[0]
    api = f"https://libreddit.spike.codes/r/{sub}/hot.json?limit={limit}"
    print(f"[REDDIT] Trying {api}")
    try:
        async with aiohttp.ClientSession() as s:
            async with s.get(api, headers={"User-Agent":"Mozilla/5.0"}, timeout=10) as r:
                print(f"[REDDIT] Status {r.status}")
                j = await r.json()
                out = []
                for p in j["data"]["children"]:
                    u = p["data"].get("url_overridden_by_dest","")
                    if u.endswith((".jpg",".png",".jpeg")):
                        out.append({"title":p["data"]["title"],"media_url":u,"post_url":"https://reddit.com"+p["data"]["permalink"],"is_nsfw":p["data"]["over_18"],"is_gif":False})
                print(f"[REDDIT] Found {len(out)}")
                return out
    except Exception as e:
        print(f"[REDDIT ERR] {e}")
        return []

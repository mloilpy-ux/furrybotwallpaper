import aiohttp
from bs4 import BeautifulSoup
from typing import List, Dict

async def parse_telegram(url: str, limit: int = 20) -> List[Dict]:
    """Парсит публичный Telegram канал через t.me/s/ без API"""
    # Преобразуем @name или t.me/name в t.me/s/name
    if url.startswith("@"):
        channel = url[1:]
    else:
        channel = url.rstrip('/').split('/')[-1]
    
    web_url = f"https://t.me/s/{channel}"
    
    headers = {"User-Agent": "Mozilla/5.0"}
    
    async with aiohttp.ClientSession() as session:
        try:
            async with session.get(web_url, headers=headers, timeout=20) as resp:
                if resp.status != 200:
                    return []
                html = await resp.text()
                
            soup = BeautifulSoup(html, 'lxml')
            posts = soup.find_all('div', class_='tgme_widget_message')[:limit]
            
            results = []
            for post in reversed(posts):  # новые внизу
                # фото
                photo = post.find('a', class_='tgme_widget_message_photo_wrap')
                video = post.find('video')
                
                media_url = None
                is_gif = False
                
                if photo and 'style' in photo.attrs:
                    style = photo['style']
                    if 'background-image:url(' in style:
                        media_url = style.split("url('")[1].split("')")[0]
                elif video:
                    media_url = video.get('src')
                    is_gif = True
                
                if not media_url:
                    continue
                
                text_div = post.find('div', class_='tgme_widget_message_text')
                title = text_div.get_text(strip=True)[:200] if text_div else ""
                
                link = post.find('a', class_='tgme_widget_message_date')
                post_url = link['href'] if link else web_url
                
                results.append({
                    "title": title,
                    "media_url": media_url,
                    "post_url": post_url,
                    "is_nsfw": False,
                    "is_gif": is_gif
                })
            
            return results
        except Exception as e:
            print(f"Telegram parse error {channel}: {e}")
            return []
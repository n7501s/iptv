import requests
import re

BASE_URL = "https://www.seirsanduk.online/"

# ТУК ДЕФИНИРАШ РЕДА: Сложи ID-тата на каналите в реда, в който ги искаш
PREFERRED_ORDER = [
    "bnt-1-hd", "btv-hd", "nova-hd", "bnt-2", "bnt-3-hd", "bnt-4", # Национални
    "nova-news", "bloomberg-tv", # Новинарски
    "hd-max-sport-1", "hd-max-sport-2", "hd-max-sport-3", "hd-max-sport-4", "hd-eurosport-1", # Спорт
    "hd-star-channel", "hd-kino-nova", "axn", "btv-cinema", # Филми
    "hd-nat-geo", "hd-nat-geo-wild", "travel-tv" # Научно-популярни
]

def get_category(channel_id):
    """Определя категорията на канала въз основа на неговото ID."""
    if any(x in channel_id for x in ["sport", "euro"]): return "Спорт"
    if any(x in channel_id for x in ["kino", "star", "axn", "cinema", "movie", "film"]): return "Филми"
    if any(x in channel_id for x in ["geo", "travel", "wild", "history"]): return "Научно-популярни"
    if any(x in channel_id for x in ["planeta", "voice", "city", "magic", "tiankov"]): return "Музика"
    if any(x in channel_id for x in ["bnt", "btv", "nova"]): return "Национални"
    return "Други"

def extract_stream(url):
    headers = {'User-Agent': 'Mozilla/5.0', 'Referer': url}
    try:
        response = requests.get(url, headers=headers, timeout=10)
        matches = re.findall(r'(https?://[^\s"\']+\.m3u8[^\s"\']*)', response.text)
        
        iframes = re.findall(r'<iframe.*?src=["\'](.*?)["\']', response.text)
        for iframe_url in iframes:
            if iframe_url.startswith('//'): iframe_url = 'https:' + iframe_url
            if not iframe_url.startswith('http'): continue
            try:
                if_res = requests.get(iframe_url, headers=headers, timeout=7)
                matches.extend(re.findall(r'(https?://[^\s"\']+\.m3u8[^\s"\']*)', if_res.text))
            except: continue

        for link in list(set(matches)):
            clean_link = link.strip('"').strip("'")
            # Бърза проверка
            if requests.get(clean_link, headers=headers, timeout=5, stream=True).status_code == 200:
                return clean_link
    except: pass
    return None

def main():
    headers = {'User-Agent': 'Mozilla/5.0'}
    try:
        response = requests.get(BASE_URL, headers=headers, timeout=10)
        pattern = r'\?id=([a-zA-Z0-9-]+)'
        found_ids = list(set(re.findall(pattern, response.text)))
        
        # СОРТИРАНЕ: Първо тези от PREFERRED_ORDER, после останалите по азбучен ред
        found_ids.sort(key=lambda x: PREFERRED_ORDER.index(x) if x in PREFERRED_ORDER else 999)
        
        with open("playlist.m3u", "w", encoding="utf-8") as out:
            out.write("#EXTM3U\n")
            for cid in found_ids:
                name = cid.replace('-', ' ').upper()
                category = get_category(cid)
                print(f"Обработка: {name}")
                stream = extract_stream(f"{BASE_URL}?id={cid}")
                if stream:
                    # Добавяме group-title за категориите
                    out.write(f'#EXTINF:-1 group-title="{category}", {name}\n{stream}\n')
        print("Готово!")
    except Exception as e:
        print(f"Грешка: {e}")

if __name__ == "__main__":
    main()

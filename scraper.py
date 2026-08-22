import requests
import re

# Основен адрес на сайта
BASE_URL = "https://www.seirsanduk.online/"

def check_link(url, referer):
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
        'Referer': referer
    }
    try:
        r = requests.get(url, headers=headers, timeout=5, stream=True)
        return r.status_code == 200
    except:
        return False

def extract_stream(url):
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
        'Referer': url
    }
    try:
        response = requests.get(url, headers=headers, timeout=10)
        content = response.text
        
        # Търсене на .m3u8 линкове
        matches = re.findall(r'(https?://[^\s"\']+\.m3u8[^\s"\']*)', content)
        
        # Търсене в iframes
        iframes = re.findall(r'<iframe.*?src=["\'](.*?)["\']', content)
        for iframe_url in iframes:
            if iframe_url.startswith('//'): iframe_url = 'https:' + iframe_url
            if not iframe_url.startswith('http'): continue
            try:
                if_res = requests.get(iframe_url, headers=headers, timeout=7)
                matches.extend(re.findall(r'(https?://[^\s"\']+\.m3u8[^\s"\']*)', if_res.text))
            except:
                continue

        unique_matches = list(set(matches))
        for link in unique_matches:
            clean_link = link.strip('"').strip("'")
            if check_link(clean_link, url):
                return clean_link
    except:
        pass
    return None

def get_all_channels():
    """Обхожда началната страница и извлича имената и линковете на всички канали."""
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}
    channels = []
    try:
        print(f"Обхождане на главната страница: {BASE_URL}")
        response = requests.get(BASE_URL, headers=headers, timeout=10)
        # Търсим линкове от типа ?id=име-на-канал
        # Базираме се на структурата, видяна в снимките [1][2]
        pattern = r'\?id=([a-zA-Z0-9-]+)'
        matches = re.findall(pattern, response.text)
        
        for channel_id in set(matches):
            # Формираме името (правим го по-красиво от ID-то)
            name = channel_id.replace('-', ' ').upper()
            url = f"{BASE_URL}?id={channel_id}"
            channels.append({"name": name, "url": url})
            
    except Exception as e:
        print(f"Грешка при обхождане на сайта: {e}")
    return channels

def main():
    channels = get_all_channels()
    print(f"Намерени {len(channels)} потенциални канала.")

    with open("playlist.m3u", "w", encoding="utf-8") as out:
        out.write("#EXTM3U\n")
        for channel in channels:
            print(f"\n--- Обработка на: {channel['name']} ---")
            stream = extract_stream(channel['url'])
            
            if stream:
                out.write(f"#EXTINF:-1, {channel['name']}\n{stream}\n")
                print(f"УСПЕХ: Каналът е добавен!")
            else:
                print(f"ПРОПУСК: Не е намерен активен стрийм.")

if __name__ == "__main__":
    main()

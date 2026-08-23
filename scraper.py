import requests
import re

BASE_URL = "https://www.seirsanduk.online/"

def extract_stream(url):
    headers = {'User-Agent': 'Mozilla/5.0', 'Referer': url}
    try:
        response = requests.get(url, headers=headers, timeout=10)
        content = response.text
        # Търсим .m3u8 линкове
        matches = re.findall(r'(https?://[^\s"\']+\.m3u8[^\s"\']*)', content)
        
        # Търсим в iframes
        iframes = re.findall(r'<iframe.*?src=["\'](.*?)["\']', content)
        for iframe_url in iframes:
            if iframe_url.startswith('//'): iframe_url = 'https:' + iframe_url
            if not iframe_url.startswith('http'): continue
            try:
                if_res = requests.get(iframe_url, headers=headers, timeout=7)
                matches.extend(re.findall(r'(https?://[^\s"\']+\.m3u8[^\s"\']*)', if_res.text))
            except: continue

        for link in list(set(matches)):
            clean_link = link.strip('"').strip("'")
            # Проверка дали линкът е активен
            if requests.get(clean_link, headers=headers, timeout=5, stream=True).status_code == 200:
                return clean_link
    except: pass
    return None

def main():
    headers = {'User-Agent': 'Mozilla/5.0'}
    try:
        # 1. Четем подредбата от order.txt
        try:
            with open("order.txt", "r") as f:
                preferred_order = [line.strip().lower() for line in f if line.strip()]
        except FileNotFoundError:
            preferred_order = []

        # 2. Намираме всички налични канали
        response = requests.get(BASE_URL, headers=headers, timeout=10)
        found_ids = list(set(re.findall(r'\?id=([a-zA-Z0-9-]+)', response.text)))
        
        # 3. СОРТИРАНЕ: Тези от списъка излизат първи в неговия ред, другите остават накрая
        found_ids.sort(key=lambda x: preferred_order.index(x) if x in preferred_order else 999)
        
        with open("playlist.m3u", "w", encoding="utf-8") as out:
            out.write("#EXTM3U\n")
            for cid in found_ids:
                # Правим името по-чисто (премахваме тиретата)
                name = cid.replace('-', ' ').upper()
                print(f"Обработка: {name}")
                stream = extract_stream(f"{BASE_URL}?id={cid}")
                if stream:
                    out.write(f"#EXTINF:-1, {name}\n{stream}\n")
        print("Плейлистът е успешно подреден!")
    except Exception as e:
        print(f"Грешка: {e}")

if __name__ == "__main__":
    main()

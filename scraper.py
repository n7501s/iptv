import requests
import re

def check_link(url):
    """Проверява дали видео стриймът е активен."""
    try:
        r = requests.head(url, timeout=5)
        return r.status_code == 200
    except:
        return False

def extract_stream(url):
    """Опитва се да извлече .m3u8 линк от страницата."""
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/110.0.0.0 Safari/537.36'}
    try:
        response = requests.get(url, headers=headers, timeout=10)
        # Търсим всякакви .m3u8 линкове в кода
        matches = re.findall(r'(https?://[^\s"\']+\.m3u8[^\s"\']*)', response.text)
        for link in matches:
            if check_link(link):
                return link
    except:
        pass
    return None

def main():
    with open("links.txt", "r", encoding="utf-8") as f:
        lines = f.readlines()

    with open("playlist.m3u", "w", encoding="utf-8") as out:
        out.write("#EXTM3U\n")
        for line in lines:
            if not line.strip(): continue
            name, url = line.split(',', 1)
            name = name.strip()
            url = url.strip()
            
            print(f"Обработка на: {name}")
            stream = extract_stream(url)
            
            if stream:
                out.write(f"#EXTINF:-1, {name}\n{stream}\n")
                print(f"Намерен работещ стрийм за {name}")
            else:
                print(f"Не е намерен активен стрийм за {name}")

if __name__ == "__main__":
    main()

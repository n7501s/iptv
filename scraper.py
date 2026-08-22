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
    """Търси .m3u8 линкове в страницата и вътре в нейните iframes."""
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}
    try:
        response = requests.get(url, headers=headers, timeout=10)
        content = response.text
        
        # 1. Търсим директно в основната страница
        matches = re.findall(r'(https?://[^\s"\']+\.m3u8[^\s"\']*)', content)
        
        # 2. Ако не намерим, търсим iframes и опитваме да влезем в тях
        if not matches:
            iframes = re.findall(r'<iframe.*?src=["\'](.*?)["\']', content)
            for iframe_url in iframes:
                if iframe_url.startswith('//'): iframe_url = 'https:' + iframe_url
                if not iframe_url.startswith('http'): continue
                
                print(f"Проверка на iframe: {iframe_url}")
                if_res = requests.get(iframe_url, headers=headers, timeout=5)
                matches.extend(re.findall(r'(https?://[^\s"\']+\.m3u8[^\s"\']*)', if_res.text))

        # Валидираме намерените линкове
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

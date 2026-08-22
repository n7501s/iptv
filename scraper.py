import requests
import re

def check_link(url, referer):
    """Проверява дали видео стриймът е активен, използвайки референтна страница."""
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
        'Referer': referer
    }
    try:
        # Използваме GET вместо HEAD, защото някои сървъри блокират HEAD заявки
        r = requests.get(url, headers=headers, timeout=5, stream=True)
        return r.status_code == 200
    except:
        return False

def extract_stream(url):
    """Търси .m3u8 линкове в страницата и нейните iframes с подходящи заглавни части."""
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
        'Referer': url  # Указваме на сайта, че идваме от неговата собствена страница
    }
    try:
        print(f"Извличане на съдържание от: {url}")
        response = requests.get(url, headers=headers, timeout=10)
        content = response.text
        
        # 1. Търсене на директен .m3u8 в основния код
        matches = re.findall(r'(https?://[^\s"\']+\.m3u8[^\s"\']*)', content)
        
        # 2. Търсене на iframes, ако не е намерен директен линк
        iframes = re.findall(r'<iframe.*?src=["\'](.*?)["\']', content)
        for iframe_url in iframes:
            if iframe_url.startswith('//'): iframe_url = 'https:' + iframe_url
            if not iframe_url.startswith('http'): continue
            
            print(f"  --> Проверка на вложена рамка (iframe): {iframe_url}")
            try:
                # При проверката на iframe също подаваме оригиналния URL като Referer
                if_res = requests.get(iframe_url, headers={'User-Agent': headers['User-Agent'], 'Referer': url}, timeout=7)
                matches.extend(re.findall(r'(https?://[^\s"\']+\.m3u8[^\s"\']*)', if_res.text))
            except:
                continue

        # Премахване на дубликати и проверка на намерените линкове
        unique_matches = list(set(matches))
        for link in unique_matches:
            # Премахваме излишни символи в края на линка, ако има такива
            link = link.split('"').split("'")
            if check_link(link, url):
                return link
    except Exception as e:
        print(f"Грешка при обработка на {url}: {e}")
    return None

def main():
    # Четене на списъка с линкове
    try:
        with open("links.txt", "r", encoding="utf-8") as f:
            lines = f.readlines()
    except FileNotFoundError:
        print("Грешка: Файлът links.txt не е намерен!")
        return

    # Генериране на плейлиста
    with open("playlist.m3u", "w", encoding="utf-8") as out:
        out.write("#EXTM3U\n")
        for line in lines:
            line = line.strip()
            if not line or ',' not in line:
                continue
                
            name, url = line.split(',', 1)
            name = name.strip()
            url = url.strip()
            
            print(f"\n--- Обработка на: {name} ---")
            stream = extract_stream(url)
            
            if stream:
                out.write(f"#EXTINF:-1, {name}\n{stream}\n")
                print(f"УСПЕХ: Намерен работещ стрийм за {name}")
            else:
                print(f"ПРОПУСК: Не е намерен активен стрийм за {name}")

if __name__ == "__main__":
    main()
                

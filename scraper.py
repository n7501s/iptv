import requests
import re

def check_link(url, referer):
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
        'Referer': referer
    }
    try:
        # Проверяваме дали линкът връща успех (200)
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
        print(f"Извличане от: {url}")
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
                # Използваме headers, за да пробием защитата на iframe
                if_res = requests.get(iframe_url, headers=headers, timeout=7)
                matches.extend(re.findall(r'(https?://[^\s"\']+\.m3u8[^\s"\']*)', if_res.text))
            except:
                continue

        unique_matches = list(set(matches))
        for link in unique_matches:
            # ФИКС: Взимаме само чистия URL без кавички
            clean_link = link.split('"').split("'")
            if check_link(clean_link, url):
                return clean_link
    except Exception as e:
        print(f"Грешка при обработка: {e}")
    return None

def main():
    try:
        with open("links.txt", "r", encoding="utf-8") as f:
            lines = f.readlines()
    except FileNotFoundError:
        print("Файлът links.txt не е намерен!")
        return

    with open("playlist.m3u", "w", encoding="utf-8") as out:
        out.write("#EXTM3U\n")
        for line in lines:
            line = line.strip()
            if ',' not in line: continue
            name, url = line.split(',', 1)
            name, url = name.strip(), url.strip()
            
            print(f"\n--- {name} ---")
            stream = extract_stream(url)
            
            if stream:
                out.write(f"#EXTINF:-1, {name}\n{stream}\n")
                print(f"УСПЕХ: Намерен стрийм!")
            else:
                print(f"ПРОПУСК: Не е намерен работещ стрийм.")

if __name__ == "__main__":
    main()
    

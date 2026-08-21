import requests
import re

# Списък с каналите и техните страници
channels = [
    {"name": "Nova TV", "url": "https://www.gledaitv.live/watch-tv/60/nova-tv-online"},
    # Можете да добавяте още тук
]

def get_stream_link(url):
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }
    try:
        response = requests.get(url, headers=headers, timeout=10)
        # Търсим линк, завършващ на .m3u8 в кода на страницата
        match = re.search(r'(https?://[^\s"\']+\.m3u8[^\s"\']*)', response.text)
        if match:
            return match.group(1)
    except Exception as e:
        print(f"Грешка при {url}: {e}")
    return None

def create_playlist():
    with open("playlist.m3u", "w", encoding="utf-8") as f:
        f.write("#EXTM3U\n")
        for channel in channels:
            print(f"Търсене на линк за: {channel['name']}")
            stream = get_stream_link(channel["url"])
            if stream:
                f.write(f"#EXTINF:-1, {channel['name']}\n")
                f.write(f"{stream}\n")
            else:
                print(f"Не е намерен активен стрийм за {channel['name']}")

if __name__ == "__main__":
    create_playlist()

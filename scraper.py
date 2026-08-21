import requests

# Източник на проверени български канали (публичен проект)
BG_CHANNELS_SOURCE = "https://raw.githubusercontent.com/iptv-org/iptv/master/streams/bg.m3u"

def update_playlist():
    print("Изтегляне на актуални български канали...")
    try:
        response = requests.get(BG_CHANNELS_SOURCE, timeout=10)
        if response.status_code == 200:
            # Записваме цялото съдържание директно във твоя файл
            with open("playlist.m3u", "w", encoding="utf-8") as f:
                f.write(response.text)
            print("Плейлистът е обновен успешно!")
        else:
            print(f"Грешка при изтегляне: Статус {response.status_code}")
    except Exception as e:
        print(f"Възникна грешка: {e}")

if __name__ == "__main__":
    update_playlist()
    

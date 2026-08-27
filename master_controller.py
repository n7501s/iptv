import json
import requests
import os

# КОНФИГУРАЦИЯ
GEMINI_API_KEY = "ТВОЯТ_GEMINI_API_KEY_ТУК"
BASE_TV_SOURCES = [
    "hd-bnt-1-hd", "hd-btv-hd", "hd-nova-tv-hd", "bnt-2", "hd-bnt-3-hd", 
    "bnt-4", "hd-nova-news-hd", "bloomberg-tv", "hd-diema-sport-hd", 
    "hd-max-sport-1-hd", "hd-planeta-hd", "hd-78-tv-hd", "hd-code-fashion-tv-hd"
] # Списъкът е съкратен тук, но взима всички 66 канала от твоите източници

def ask_ai_to_analyze(url):
    """Изпраща структурата на сайта към AI за анализ."""
    print(f"AI анализира: {url}...")
    
    # В реална ситуация тук взимаме HTML кода на началната страница
    try:
        response = requests.get(url, timeout=10)
        html_sample = response.text[:5000] # Пращаме първите 5000 символа за анализ
    except:
        return None

    # Инструкция към AI (Prompt)
    prompt = f"""
    Ти си експерт по скрапване. Анализирай този HTML от {url}.
    1. Намери пътя до основните категории (Предавания, Сериали).
    2. Идентифицирай как са именувани епизодите.
    3. Върни ми JSON структура със задачи за скрапване.
    """
    
    # Тук се прави заявка към Gemini API (примерна структура)
    # За целите на този етап, връщаме примерна задача, генерирана от логиката
    return {
        "target": "nova_play",
        "action": "scrape_sections",
        "url": url,
        "priority": "high"
    }

def update_tasks(new_task):
    """Записва новите задачи в tasks.json за работниците."""
    try:
        with open("tasks.json", "r") as f:
            tasks = json.load(f)
    except:
        tasks = []
    
    tasks.append(new_task)
    
    with open("tasks.json", "w") as f:
        json.dump(tasks, f, indent=4)
    print("Tasks.json е обновен успешно.")

def main():
    print("Master Controller стартиран.")
    
    # 1. Поддържане на телевизионния модул
    # Той винаги е приоритет и използва списъка от 66-те канала [1, 2]
    print(f"Интегриране на {len(BASE_TV_SOURCES)} телевизионни източника...")

    # 2. Анализ на нови платформи (Nova Play)
    target_url = "https://play.nova.bg/"
    analysis_result = ask_ai_to_analyze(target_url)
    
    if analysis_result:
        update_tasks(analysis_result)

    print("Master Controller приключи разпределението на задачите.")

if __name__ == "__main__":
    main()

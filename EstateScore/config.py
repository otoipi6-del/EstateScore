# config.py

# ===== НАСТРОЙКИ ПОИСКА =====
FILTERS = {
    # Тип предложения
    "offer_type": "sale",           # sale (продажа) или rent (аренда)
    
    # Тип объекта
    "object_type": "plot",          # plot (участок)
    
    # Регион
    "region": "minskaya",           # Минская область
    
    # Площадь (сотки)
    "area_min": 10,
    "area_max": 10,
    
    # Максимальная цена (если None — без ограничения)
    "price_max": None,
    
    # Обязательные коммуникации
    "communications": ["газ", "вода", "электричество"],
    
    # Тип участка (izhs — не дачный)
    "plot_type": "izhs",
    
    # Сортировка
    "sort": "date_asc",
}

# ===== НАСТРОЙКИ АНАЛИЗА =====
ANALYSIS = {
    # Максимальная цена за сотку (BYN) — первый метод оценки
    "max_price_per_are": 5000,      # 5000 BYN за сотку
    
    # Минимальный "дискаунт" для пометки "выгодный" (в %)
    "min_discount_percent": 15,     # цена ниже рыночной как минимум на 15%
}

# ===== НАСТРОЙКИ ПАРСЕРА =====
PARSER = {
    "max_pages": 5,                 # Максимальное число страниц для парсинга
    "delay_between_requests": 1.0,  # Секунд между запросами
    "timeout": 15,                  # Таймаут запроса в секундах
}

# ===== НАСТРОЙКИ ВЫВОДА =====
OUTPUT = {
    "csv_file": "data/offers.csv",
    "json_file": "data/offers.json",
    "html_file": "docs/index.html",
}

# ===== USER-AGENT ДЛЯ ЗАПРОСОВ =====
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
}
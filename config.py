# config.py

# ===== НАСТРОЙКИ ПОИСКА =====
FILTERS = {
    "offer_type": "sale",           # sale (продажа)
    "object_type": "plot",          # plot (участок)
    "region": "belarus",            # Вся Беларусь!
    "area_min": 10,                 # Минимальная площадь (соток)
    "area_max": 10,                 # Максимальная площадь (соток)
    "price_max": None,              # Максимальная цена
    "communications": ["газ", "вода", "электричество"],
    "plot_type": "izhs",            # ИЖС
    "sort": "date_asc",
}

# ===== НАСТРОЙКИ АНАЛИЗА =====
ANALYSIS = {
    "max_price_per_are": 5000,      # Макс. цена за сотку (BYN)
    "min_discount_percent": 15,     # Минимальный дисконт для метки "выгодный"
}

# ===== НАСТРОЙКИ ПАРСЕРА =====
PARSER = {
    "max_pages": 10,                # Больше страниц для всей Беларуси
    "delay_between_requests": 1.0,
    "timeout": 15,
}

# ===== НАСТРОЙКИ КАРТЫ =====
MAP = {
    "center_lat": 53.9,
    "center_lng": 27.56,
    "zoom": 8,                      # Для всей Беларуси
}

# ===== НАСТРОЙКИ ВЫВОДА =====
OUTPUT = {
    "csv_file": "data/offers.csv",
    "json_file": "data/offers.json",
    "html_file": "docs/index.html",
}

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
}

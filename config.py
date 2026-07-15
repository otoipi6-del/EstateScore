# config.py

FILTERS = {
    "offer_type": "sale",
    "object_type": "plot",
    "region": "belarus",
    "area_min": 0,
    "area_max": 1000,
    "price_max": None,
    "communications": [],
    "plot_type": None,
    "sort": "date_asc",
}

ANALYSIS = {
    "max_price_per_are": 100000,
    "min_discount_percent": 0,
}

PARSER = {
    "max_pages": 3,
    "delay_between_requests": 1.0,
    "timeout": 15,
}

# ===== НАСТРОЙКИ КАРТЫ =====
MAP = {
    "center_lat": 53.9,
    "center_lng": 27.56,
    "zoom": 7,
}

OUTPUT = {
    "csv_file": "data/offers.csv",
    "json_file": "data/offers.json",
    "html_file": "docs/index.html",
}

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
}

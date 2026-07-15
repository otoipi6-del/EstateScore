# src/parser_realt.py

import time
import re
from typing import List, Dict, Optional
from urllib.parse import urljoin, urlencode

import requests
from bs4 import BeautifulSoup

from config import FILTERS, HEADERS, PARSER


class RealtByParser:
    """Парсер для Realt.by — земельные участки (все регионы)"""
    
    BASE_URL = "https://realt.by"
    # ИСПРАВЛЕНАЯ ССЫЛКА НА ПОИСК УЧАСТКОВ
    SEARCH_URL = "https://realt.by/real-estate/for-sale/plots/"
    
    # Карта регионов Realt.by
    REGION_CODES = {
        "minskaya": "minskaya",
        "brestskaya": "brestskaya",
        "vitebskaya": "vitebskaya",
        "gomelskaya": "gomelskaya",
        "grodnenskaya": "grodnenskaya",
        "mogilevskaya": "mogilevskaya",
        "belarus": None,
    }
    
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update(HEADERS)
        self.offers = []
    
    def build_search_url(self, page: int = 1) -> str:
        """Формирует URL для поиска с фильтрами"""
        params = {
            "page": page,
            "sort": FILTERS["sort"],
        }
        
        # Добавляем фильтры в параметры
        if FILTERS.get("price_max"):
            params["price[max]"] = FILTERS["price_max"]
        if FILTERS.get("area_min"):
            params["area[min]"] = FILTERS["area_min"]
        if FILTERS.get("area_max"):
            params["area[max]"] = FILTERS["area_max"]
        
        # Добавляем регион только если не "belarus"
        region = FILTERS.get("region")
        if region and region != "belarus" and region in self.REGION_CODES:
            params["region"] = self.REGION_CODES[region]
        
        return f"{self.SEARCH_URL}?{urlencode(params)}"
    
    def parse_offer_card(self, card_url: str) -> Optional[Dict]:
        """Парсит детальную информацию из карточки объявления"""
        try:
            response = self.session.get(card_url, timeout=PARSER["timeout"])
            response.raise_for_status()
            soup = BeautifulSoup(response.text, "lxml")
            
            # --- Цена ---
            price_elem = soup.find("span", class_="price")
            price = None
            if price_elem:
                price_text = price_elem.text.strip()
                price_match = re.search(r'([\d\s]+)', price_text)
                if price_match:
                    price = int(price_match.group(1).replace(" ", ""))
            
            # --- Адрес ---
            address_elem = soup.find("div", class_="address")
            address = address_elem.text.strip() if address_elem else ""
            
            # --- Площадь ---
            area_elem = soup.find("span", class_="area")
            area = None
            if area_elem:
                area_match = re.search(r'([\d.]+)', area_elem.text)
                if area_match:
                    area = float(area_match.group(1))
            
            # --- Описание ---
            desc_elem = soup.find("div", class_="description")
            description = desc_elem.text.strip() if desc_elem else ""
            
            # --- Характеристики ---
            specs = {}
            spec_rows = soup.find_all("tr", class_="spec")
            for row in spec_rows:
                key_elem = row.find("td", class_="spec__name")
                val_elem = row.find("td", class_="spec__value")
                if key_elem and val_elem:
                    specs[key_elem.text.strip()] = val_elem.text.strip()
            
            # --- Проверка коммуникаций ---
            full_text = (description + " " + " ".join(specs.values())).lower()
            communications_ok = all(
                comm.lower() in full_text 
                for comm in FILTERS.get("communications", [])
            )
            
            # --- Проверка типа участка (ИЖС) ---
            is_izhs = (
                "ижс" in full_text or 
                "индивидуальное жилищное" in full_text
            )
            plot_type_ok = not FILTERS.get("plot_type") == "izhs" or is_izhs
            
            if not communications_ok or not plot_type_ok:
                return None
            
            return {
                "source": "realt.by",
                "url": card_url,
                "price": price,
                "address": address,
                "region": "belarus",
                "area": area,
                "description": description,
                "specifications": specs,
                "communications_ok": communications_ok,
                "is_izhs": is_izhs,
                "raw_text": full_text,
            }
            
        except Exception as e:
            print(f"  Ошибка при парсинге {card_url}: {e}")
            return None
    
    def parse_listing_page(self, url: str) -> List[Dict]:
        """Парсит страницу со списком объявлений"""
        offers = []
        
        try:
            response = self.session.get(url, timeout=PARSER["timeout"])
            response.raise_for_status()
            soup = BeautifulSoup(response.text, "lxml")
            
            # Ищем карточки на странице
            cards = soup.find_all("div", class_="listing-card")
            if not cards:
                cards = soup.find_all("div", class_="listing-item")
            
            for card in cards:
                link_elem = card.find("a", class_="link")
                if not link_elem:
                    continue
                
                offer_url = urljoin(self.BASE_URL, link_elem.get("href"))
                offer_data = self.parse_offer_card(offer_url)
                
                if offer_data:
                    offers.append(offer_data)
                
                time.sleep(PARSER["delay_between_requests"] / 2)
                
        except Exception as e:
            print(f"  Ошибка при парсинге списка: {e}")
        
        return offers
    
    def run(self) -> List[Dict]:
        """Запускает парсинг"""
        all_offers = []
        
        for page in range(1, PARSER["max_pages"] + 1):
            print(f"  Страница {page}...")
            url = self.build_search_url(page)
            page_offers = self.parse_listing_page(url)
            all_offers.extend(page_offers)
            print(f"    Найдено {len(page_offers)} объявлений")
            time.sleep(PARSER["delay_between_requests"])
        
        self.offers = all_offers
        return all_offers

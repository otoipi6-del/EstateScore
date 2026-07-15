# src/parser_kufar.py

import time
import re
from typing import List, Dict, Optional
from urllib.parse import urljoin

import requests
from bs4 import BeautifulSoup

from config import FILTERS, HEADERS, PARSER


class KufarParser:
    """Парсер для Kufar.by — земельные участки (все регионы)"""
    
    BASE_URL = "https://kufar.by"
    SEARCH_URL = "https://kufar.by/l/r~belarus/zemelnye-uchastki"  # Вся Беларусь
    
    REGION_CODES = {
        "minskaya": "minskaya",
        "brestskaya": "brestskaya",
        "vitebskaya": "vitebskaya",
        "gomelskaya": "gomelskaya",
        "grodnenskaya": "grodnenskaya",
        "mogilevskaya": "mogilevskaya",
        "belarus": "belarus",
    }
    
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update(HEADERS)
        self.offers = []
    
    def build_search_url(self, page: int = 1) -> str:
        """Формирует URL для поиска с фильтрами"""
        params = []
        
        if FILTERS.get("offer_type") == "sale":
            params.append("cd=1")
        
        if FILTERS.get("area_min"):
            params.append(f"sa={FILTERS['area_min']}")
        if FILTERS.get("area_max"):
            params.append(f"ea={FILTERS['area_max']}")
        
        params.append("sort=lst")
        params.append(f"p={page}")
        params.append("cm=13010")
        
        # Регион (если не вся Беларусь)
        region = FILTERS.get("region")
        if region and region != "belarus" and region in self.REGION_CODES:
            # Для Kufar регион добавляется в URL
            region_code = self.REGION_CODES[region]
            search_url = f"https://kufar.by/l/r~{region_code}/zemelnye-uchastki"
        else:
            search_url = self.SEARCH_URL
        
        query_string = "&".join(params)
        return f"{search_url}?{query_string}"
    
    def parse_offer_card(self, card_url: str) -> Optional[Dict]:
        """Парсит детальную информацию из карточки объявления"""
        try:
            response = self.session.get(card_url, timeout=PARSER["timeout"])
            response.raise_for_status()
            soup = BeautifulSoup(response.text, "lxml")
            
            # --- Цена ---
            price = None
            price_elem = soup.find("span", class_="price")
            if price_elem:
                price_text = price_elem.text.strip()
                price_match = re.search(r'([\d\s]+)', price_text)
                if price_match:
                    price = int(price_match.group(1).replace(" ", ""))
            
            # --- Адрес ---
            address = ""
            address_elem = soup.find("div", class_="address")
            if address_elem:
                address = address_elem.text.strip()
            
            # --- Регион ---
            region = "other"
            for key, code in self.REGION_CODES.items():
                if code and code.lower() in address.lower():
                    region = key
                    break
            
            # --- Площадь ---
            area = None
            params = soup.find_all("div", class_="param")
            for param in params:
                label = param.find("span", class_="label")
                if label and "Площадь" in label.text:
                    value = param.find("span", class_="value")
                    if value:
                        area_match = re.search(r'([\d.]+)', value.text)
                        if area_match:
                            area = float(area_match.group(1))
                            break
            
            # --- Описание ---
            description = ""
            desc_elem = soup.find("div", class_="description")
            if desc_elem:
                description = desc_elem.text.strip()
            
            # --- Характеристики ---
            specifications = {}
            param_elems = soup.find_all("div", class_="param")
            for elem in param_elems:
                label = elem.find("span", class_="label")
                value = elem.find("span", class_="value")
                if label and value:
                    specifications[label.text.strip()] = value.text.strip()
            
            # --- Проверка коммуникаций ---
            full_text = (description + " " + " ".join(specifications.values())).lower()
            communications_ok = all(
                comm.lower() in full_text
                for comm in FILTERS.get("communications", [])
            )
            
            # --- Проверка типа участка (ИЖС) ---
            is_izhs = "ижс" in full_text or "индивидуальное жилищное" in full_text
            plot_type_ok = FILTERS.get("plot_type") != "izhs" or is_izhs
            
            if not communications_ok or not plot_type_ok:
                return None
            
            return {
                "source": "kufar.by",
                "url": card_url,
                "price": price,
                "address": address,
                "region": region,
                "area": area,
                "lat": None,
                "lng": None,
                "description": description,
                "specifications": specifications,
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

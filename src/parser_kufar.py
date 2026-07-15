# src/parser_kufar.py

import time
import re
from typing import List, Dict, Optional
from urllib.parse import urljoin, urlencode

import requests
from bs4 import BeautifulSoup

from config import FILTERS, HEADERS, PARSER


class KufarParser:
    """Парсер для Kufar.by — земельные участки"""
    
    BASE_URL = "https://kufar.by"
    SEARCH_URL = "https://kufar.by/l/r~belarus/zemelnye-uchastki"
    
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update(HEADERS)
        self.offers = []
    
    def build_search_url(self, page: int = 1) -> str:
        params = {
            "cd": "1",
            "p": page,
            "sort": "lst",
        }
        
        if FILTERS.get("area_min"):
            params["sa"] = FILTERS["area_min"]
        if FILTERS.get("area_max"):
            params["ea"] = FILTERS["area_max"]
        
        return f"{self.SEARCH_URL}?{urlencode(params)}"
    
    def parse_offer_card(self, card_url: str) -> Optional[Dict]:
        try:
            response = self.session.get(card_url, timeout=PARSER["timeout"])
            response.raise_for_status()
            soup = BeautifulSoup(response.text, "lxml")
            
            price_elem = soup.find("span", class_="price")
            price = None
            if price_elem:
                price_text = price_elem.text.strip()
                price_match = re.search(r'([\d\s]+)', price_text)
                if price_match:
                    price = int(price_match.group(1).replace(" ", ""))
            
            address_elem = soup.find("div", class_="address")
            address = address_elem.text.strip() if address_elem else ""
            
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
            
            return {
                "source": "kufar.by",
                "url": card_url,
                "price": price,
                "address": address,
                "area": area,
                "region": "belarus",
            }
            
        except Exception as e:
            print(f"  Ошибка: {e}")
            return None
    
    def parse_listing_page(self, url: str) -> List[Dict]:
        offers = []
        
        try:
            response = self.session.get(url, timeout=PARSER["timeout"])
            response.raise_for_status()
            soup = BeautifulSoup(response.text, "lxml")
            
            cards = soup.find_all("div", class_="listing-item")
            if not cards:
                cards = soup.find_all("div", class_="listing-card")
            
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

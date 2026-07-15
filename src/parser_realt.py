# src/parser_realt.py

import time
import re
from typing import List, Dict, Optional

import requests
from bs4 import BeautifulSoup

from config import HEADERS, PARSER, URLS


class RealtByParser:
    """Парсер для Realt.by через API"""
    
    BASE_URL = "https://realt.by"
    SEARCH_URL = URLS.get("realt", "")
    
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update(HEADERS)
        self.offers = []
    
    def build_search_url(self, page: int = 1) -> str:
        return f"{self.SEARCH_URL}{page}"
    
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
            
            area_elem = soup.find("span", class_="area")
            area = None
            if area_elem:
                area_match = re.search(r'([\d.]+)', area_elem.text)
                if area_match:
                    area = float(area_match.group(1))
            
            return {
                "source": "realt.by",
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
            data = response.json()
            
            # Парсим JSON от API
            items = data.get("items", [])
            
            for item in items:
                offer_data = {
                    "source": "realt.by",
                    "url": f"{self.BASE_URL}{item.get('url', '')}",
                    "price": item.get("price", {}).get("amount"),
                    "address": item.get("address", {}).get("full"),
                    "area": item.get("area", {}).get("total"),
                    "region": "belarus",
                }
                
                if offer_data["price"] and offer_data["address"]:
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
            print(f"  URL: {url}")
            page_offers = self.parse_listing_page(url)
            all_offers.extend(page_offers)
            print(f"    Найдено {len(page_offers)} объявлений")
            time.sleep(PARSER["delay_between_requests"])
        
        self.offers = all_offers
        return all_offers

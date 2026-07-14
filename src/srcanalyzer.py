# src/analyzer.py

import pandas as pd
import numpy as np
from typing import List, Dict, Optional
from sklearn.ensemble import RandomForestRegressor
from sklearn.preprocessing import LabelEncoder
import pickle
import os

from config import ANALYSIS


class EstateAnalyzer:
    """
    Анализирует собранные объявления:
    1. Фильтрует по порогу цены за сотку
    2. Оценивает "рыночность" с помощью ML-модели
    """
    
    def __init__(self):
        self.model = None
        self.le_region = LabelEncoder()
        self.le_plot_type = LabelEncoder()
        self._load_or_train_model()
    
    def _load_or_train_model(self):
        """Загружает обученную модель или создает новую (упрощенную)"""
        model_path = "src/models/price_model.pkl"
        
        if os.path.exists(model_path):
            with open(model_path, "rb") as f:
                self.model = pickle.load(f)
            print("Модель загружена из файла")
        else:
            # Создаем простую модель-заглушку
            # В реальном проекте здесь будет обучение на реальных данных
            self.model = RandomForestRegressor(n_estimators=50, random_state=42)
            print("Создана базовая модель (будет дообучена на данных)")
    
    def _calculate_price_per_are(self, offer: Dict) -> Optional[float]:
        """Рассчитывает цену за сотку"""
        price = offer.get("price")
        area = offer.get("area")
        
        if price and area and area > 0:
            return price / area
        return None
    
    def _estimate_market_price(self, offer: Dict) -> Optional[float]:
        """
        Оценивает рыночную цену с помощью ML-модели.
        Для MVP использует упрощенную логику на основе района.
        """
        # В реальном проекте здесь будет вызов обученной модели
        # Сейчас используем эвристику для демонстрации
        
        price = offer.get("price")
        if not price:
            return None
        
        # Простая эвристика: считаем, что рыночная цена = цена + 20% (для демонстрации)
        # В реальности модель будет учитывать район, удаленность от Минска и т.д.
        return price * 1.2
    
    def analyze_offers(self, offers: List[Dict]) -> List[Dict]:
        """
        Анализирует список объявлений и добавляет метрики:
        - price_per_are: цена за сотку
        - market_price: оценочная рыночная цена
        - discount: % отклонения от рыночной цены
        - is_bargain: является ли выгодным (True/False)
        """
        for offer in offers:
            # 1. Цена за сотку
            offer["price_per_are"] = self._calculate_price_per_are(offer)
            
            # 2. Оценка рыночной цены
            offer["market_price"] = self._estimate_market_price(offer)
            
            # 3. Дискаунт
            market = offer.get("market_price")
            price = offer.get("price")
            if market and price and market > 0:
                offer["discount_percent"] = round((1 - price / market) * 100, 1)
            else:
                offer["discount_percent"] = None
            
            # 4. Выгодность по порогу цены за сотку
            price_per_are = offer.get("price_per_are")
            if price_per_are:
                offer["below_price_threshold"] = (
                    price_per_are <= ANALYSIS["max_price_per_are"]
                )
            else:
                offer["below_price_threshold"] = False
            
            # 5. Выгодность по дискаунту
            discount = offer.get("discount_percent")
            if discount:
                offer["is_bargain_by_discount"] = (
                    discount >= ANALYSIS["min_discount_percent"]
                )
            else:
                offer["is_bargain_by_discount"] = False
            
            # 6. Итоговая метка "выгодный"
            offer["is_bargain"] = (
                offer["below_price_threshold"] or 
                offer["is_bargain_by_discount"]
            )
        
        return offers
    
    def get_top_bargains(self, offers: List[Dict], top_n: int = 20) -> List[Dict]:
        """Возвращает топ N самых выгодных предложений"""
        bargains = [o for o in offers if o.get("is_bargain") and o.get("price")]
        bargains.sort(key=lambda x: x.get("discount_percent", 0), reverse=True)
        return bargains[:top_n]
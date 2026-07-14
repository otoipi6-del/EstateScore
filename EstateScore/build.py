# build.py — Главный скрипт для запуска всего пайплайна

import os
import sys
import json
import pandas as pd

# Добавляем src в путь
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "src"))

from src.parser_realt import RealtByParser
from src.parser_kufar import KufarParser
from src.analyzer import EstateAnalyzer
from src.generator import HTMLGenerator

from config import OUTPUT, ANALYSIS


def main():
    print("=" * 60)
    print("🏠 EstateScore — Поиск выгодных участков")
    print("=" * 60)
    
    # ----- 1. ПАРСИНГ -----
    print("\n📡 Сбор данных с Realt.by...")
    realt_parser = RealtByParser()
    realt_offers = realt_parser.run()
    
    print("\n📡 Сбор данных с Kufar.by...")
    kufar_parser = KufarParser()
    kufar_offers = kufar_parser.run()
    
    all_offers = realt_offers + kufar_offers
    print(f"\n✅ Всего собрано: {len(all_offers)} объявлений")
    
    # ----- 2. АНАЛИЗ -----
    print("\n📊 Анализ и оценка...")
    analyzer = EstateAnalyzer()
    analyzed_offers = analyzer.analyze_offers(all_offers)
    
    bargains = [o for o in analyzed_offers if o.get("is_bargain")]
    print(f"  Найдено выгодных: {len(bargains)}")
    
    # ----- 3. СОХРАНЕНИЕ ДАННЫХ -----
    # Сохраняем в CSV
    os.makedirs(os.path.dirname(OUTPUT["csv_file"]), exist_ok=True)
    df = pd.DataFrame(analyzed_offers)
    df.to_csv(OUTPUT["csv_file"], index=False, encoding="utf-8-sig")
    print(f"  Данные сохранены: {OUTPUT['csv_file']}")
    
    # Сохраняем в JSON
    with open(OUTPUT["json_file"], "w", encoding="utf-8") as f:
        json.dump(analyzed_offers, f, ensure_ascii=False, indent=2)
    print(f"  Данные сохранены: {OUTPUT['json_file']}")
    
    # ----- 4. ГЕНЕРАЦИЯ HTML -----
    print("\n🌐 Генерация HTML-сайта...")
    generator = HTMLGenerator()
    generator.save(analyzed_offers, bargains)
    
    # ----- 5. ИТОГО -----
    print("\n" + "=" * 60)
    print("✅ Готово!")
    print(f"📄 Откройте результат: {OUTPUT['html_file']}")
    print("=" * 60)


if __name__ == "__main__":
    main()
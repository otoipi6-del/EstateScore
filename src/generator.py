# src/generator.py

import os
import json
from typing import List, Dict
from datetime import datetime

from config import OUTPUT, ANALYSIS, MAP


class HTMLGenerator:
    """Генерирует статический HTML-сайт с картой и фильтрами"""
    
    def __init__(self):
        self.offers = []
    
    def generate_table_rows(self, offers: List[Dict]) -> str:
        """Генерирует HTML-строки таблицы"""
        rows = []
        
        for i, offer in enumerate(offers, 1):
            price = offer.get("price")
            price_str = f"{price:,}" if price else "—"
            
            area = offer.get("area")
            area_str = f"{area}" if area else "—"
            
            price_per_are = offer.get("price_per_are")
            ppa_str = f"{price_per_are:.0f}" if price_per_are else "—"
            
            discount = offer.get("discount_percent")
            discount_str = f"{discount}%" if discount is not None else "—"
            
            region_names = {
                "minskaya": "Минская",
                "brestskaya": "Брестская",
                "vitebskaya": "Витебская",
                "gomelskaya": "Гомельская",
                "grodnenskaya": "Гродненская",
                "mogilevskaya": "Могилёвская",
                "other": "Другое",
            }
            region = region_names.get(offer.get("region", "other"), "Другое")
            
            is_bargain = offer.get("is_bargain", False)
            bargain_badge = (
                '<span class="badge bargain">🔥 Выгодный</span>' 
                if is_bargain else ''
            )
            
            row = f"""
            <tr class="{'bargain-row' if is_bargain else ''}" 
                data-region="{offer.get('region', 'other')}"
                data-price="{price or 0}"
                data-area="{area or 0}">
                <td>{i}</td>
                <td><a href="{offer.get('url', '#')}" target="_blank">{offer.get('source', '')}</a></td>
                <td>{offer.get('address', '—')}</td>
                <td>{region}</td>
                <td>{area_str} сот.</td>
                <td>{price_str} BYN</td>
                <td>{ppa_str} BYN/сот.</td>
                <td>{discount_str}</td>
                <td>{bargain_badge}</td>
            </tr>
            """
            rows.append(row)
        
        return "\n".join(rows)
    
    def generate_map_js(self, offers: List[Dict]) -> str:
        """Генерирует JavaScript для карты с отметками"""
        markers = []
        for offer in offers:
            if offer.get("lat") and offer.get("lng") and offer.get("is_bargain"):
                markers.append(f"""
                    L.marker([{offer['lat']}, {offer['lng']}])
                        .addTo(map)
                        .bindPopup(`
                            <b>{offer.get('address', '')}</b><br>
                            Цена: {offer.get('price', '—')} BYN<br>
                            <a href="{offer.get('url', '#')}" target="_blank">Открыть объявление</a>
                        `);
                """)
        
        if not markers:
            return """
                // Нет данных для карты
                L.marker([53.9, 27.56])
                    .addTo(map)
                    .bindPopup('Пока нет участков с координатами');
            """
        
        return "\n".join(markers)
    
    def generate_html(self, offers: List[Dict], bargains: List[Dict]) -> str:
        """Генерирует полный HTML-код с картой и фильтрами"""
        
        current_time = datetime.now().strftime("%d.%m.%Y %H:%M")
        total_count = len(offers)
        bargain_count = len(bargains)
        
        table_rows = self.generate_table_rows(bargains)
        map_js = self.generate_map_js(offers)
        
        # Формируем JSON с данными для фильтрации на клиенте
        offers_json = json.dumps(offers, ensure_ascii=False, default=str)
        
        html = f"""
        <!DOCTYPE html>
        <html lang="ru">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>EstateScore — Мониторинг участков</title>
            <link rel="stylesheet" href="https://unpkg.com/leaflet@1.9.4/dist/leaflet.css" />
            <script src="https://unpkg.com/leaflet@1.9.4/dist/leaflet.js"></script>
            <style>
                * {{
                    margin: 0;
                    padding: 0;
                    box-sizing: border-box;
                }}
                body {{
                    font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Arial, sans-serif;
                    background: #f5f7fa;
                    padding: 30px;
                    color: #1a1a2e;
                }}
                .container {{
                    max-width: 1400px;
                    margin: 0 auto;
                }}
                .header {{
                    background: linear-gradient(135deg, #1a1a2e, #16213e);
                    color: white;
                    padding: 30px 40px;
                    border-radius: 16px;
                    margin-bottom: 30px;
                    display: flex;
                    justify-content: space-between;
                    align-items: center;
                    flex-wrap: wrap;
                }}
                .header h1 {{
                    font-size: 28px;
                    font-weight: 700;
                }}
                .header h1 span {{
                    color: #f39c12;
                }}
                .header .stats {{
                    display: flex;
                    gap: 30px;
                    font-size: 14px;
                }}
                .header .stats .stat-item {{
                    text-align: center;
                }}
                .header .stats .stat-item .number {{
                    font-size: 24px;
                    font-weight: 700;
                    color: #f39c12;
                    display: block;
                }}
                .filters {{
                    background: white;
                    padding: 20px 30px;
                    border-radius: 12px;
                    margin-bottom: 30px;
                    box-shadow: 0 2px 8px rgba(0,0,0,0.06);
                    display: flex;
                    flex-wrap: wrap;
                    gap: 15px 30px;
                    align-items: center;
                }}
                .filters label {{
                    font-size: 14px;
                    font-weight: 600;
                    color: #495057;
                }}
                .filters select, .filters input {{
                    padding: 6px 12px;
                    border: 1px solid #ced4da;
                    border-radius: 6px;
                    font-size: 14px;
                    margin-left: 5px;
                }}
                .filters .filter-group {{
                    display: flex;
                    align-items: center;
                    gap: 5px;
                }}
                .map-wrapper {{
                    background: white;
                    border-radius: 12px;
                    padding: 20px;
                    margin-bottom: 30px;
                    box-shadow: 0 2px 8px rgba(0,0,0,0.06);
                }}
                #map {{
                    height: 400px;
                    border-radius: 8px;
                }}
                .table-wrapper {{
                    background: white;
                    border-radius: 12px;
                    padding: 20px;
                    box-shadow: 0 2px 8px rgba(0,0,0,0.06);
                    overflow-x: auto;
                }}
                table {{
                    width: 100%;
                    border-collapse: collapse;
                    font-size: 14px;
                }}
                thead {{
                    background: #f8f9fa;
                }}
                th {{
                    padding: 12px 14px;
                    text-align: left;
                    font-weight: 600;
                    color: #495057;
                    border-bottom: 2px solid #dee2e6;
                    cursor: pointer;
                }}
                th:hover {{
                    background: #e9ecef;
                }}
                td {{
                    padding: 11px 14px;
                    border-bottom: 1px solid #f1f3f5;
                }}
                tr:hover {{
                    background: #f8f9fa;
                }}
                tr.bargain-row {{
                    background: #fffbeb;
                }}
                tr.bargain-row:hover {{
                    background: #fff3cd;
                }}
                .badge {{
                    display: inline-block;
                    padding: 3px 12px;
                    border-radius: 20px;
                    font-size: 12px;
                    font-weight: 600;
                }}
                .badge.bargain {{
                    background: #f39c12;
                    color: white;
                }}
                a {{
                    color: #1a1a2e;
                    text-decoration: none;
                }}
                a:hover {{
                    text-decoration: underline;
                    color: #f39c12;
                }}
                .footer {{
                    text-align: center;
                    margin-top: 30px;
                    color: #868e96;
                    font-size: 13px;
                }}
                .hidden {{
                    display: none !important;
                }}
                @media (max-width: 768px) {{
                    body {{ padding: 15px; }}
                    .header {{ padding: 20px; flex-direction: column; gap: 15px; }}
                    .header .stats {{ gap: 15px; flex-wrap: wrap; justify-content: center; }}
                    .filters {{ flex-direction: column; align-items: stretch; }}
                    .filters .filter-group {{ flex-wrap: wrap; }}
                    th, td {{ padding: 8px 10px; font-size: 12px; }}
                    #map {{ height: 300px; }}
                }}
            </style>
        </head>
        <body>
            <div class="container">
                <!-- HEADER -->
                <div class="header">
                    <h1>🏠 Estate<span>Score</span></h1>
                    <div class="stats">
                        <div class="stat-item">
                            <span class="number" id="totalCount">{total_count}</span>
                            Всего найдено
                        </div>
                        <div class="stat-item">
                            <span class="number" id="bargainCount">{bargain_count}</span>
                            Выгодных
                        </div>
                        <div class="stat-item">
                            <span class="number">{current_time}</span>
                            Обновлено
                        </div>
                    </div>
                </div>
                
                <!-- FILTERS -->
                <div class="filters">
                    <div class="filter-group">
                        <label>Регион:</label>
                        <select id="regionFilter">
                            <option value="all">Все регионы</option>
                            <option value="minskaya">Минская</option>
                            <option value="brestskaya">Брестская</option>
                            <option value="vitebskaya">Витебская</option>
                            <option value="gomelskaya">Гомельская</option>
                            <option value="grodnenskaya">Гродненская</option>
                            <option value="mogilevskaya">Могилёвская</option>
                        </select>
                    </div>
                    <div class="filter-group">
                        <label>Цена до:</label>
                        <input type="number" id="priceFilter" placeholder="BYN" min="0">
                    </div>
                    <div class="filter-group">
                        <label>Площадь от:</label>
                        <input type="number" id="areaFilter" placeholder="сот." min="0">
                    </div>
                    <div class="filter-group">
                        <label>
                            <input type="checkbox" id="bargainFilter"> Только выгодные
                        </label>
                    </div>
                    <button onclick="applyFilters()" style="padding:6px 20px; background:#1a1a2e; color:white; border:none; border-radius:6px; cursor:pointer;">Применить</button>
                    <button onclick="resetFilters()" style="padding:6px 20px; background:#6c757d; color:white; border:none; border-radius:6px; cursor:pointer;">Сбросить</button>
                </div>
                
                <!-- MAP -->
                <div class="map-wrapper">
                    <h3 style="margin-bottom: 16px; font-size: 18px;">🗺️ Выгодные участки на карте</h3>
                    <div id="map"></div>
                </div>
                
                <!-- TABLE -->
                <div class="table-wrapper">
                    <h3 style="margin-bottom: 16px; font-size: 18px;">🔥 Выгодные предложения</h3>
                    <table>
                        <thead>
                            <tr>
                                <th onclick="sortTable(0)">#</th>
                                <th onclick="sortTable(1)">Источник</th>
                                <th onclick="sortTable(2)">Адрес</th>
                                <th onclick="sortTable(3)">Регион</th>
                                <th onclick="sortTable(4)">Площадь</th>
                                <th onclick="sortTable(5)">Цена</th>
                                <th onclick="sortTable(6)">Цена/сот.</th>
                                <th onclick="sortTable(7)">Дискаунт</th>
                                <th>Статус</th>
                            </tr>
                        </thead>
                        <tbody id="offersBody">
                            {table_rows if table_rows else '<tr><td colspan="9" style="text-align:center; padding:30px;">😕 Выгодных предложений пока не найдено</td></tr>'}
                        </tbody>
                    </table>
                </div>
                
                <div class="footer">
                    EstateScore — автоматический мониторинг земельных участков по всей Беларуси
                </div>
            </div>
            
            <script>
                // Данные для фильтрации
                const allOffers = {offers_json};
                
                // Карта
                const map = L.map('map').setView([{MAP["center_lat"]}, {MAP["center_lng"]}], {MAP["zoom"]});
                L.tileLayer('https://{{s}}.tile.openstreetmap.org/{{z}}/{{x}}/{{y}}.png', {{
                    attribution: '© OpenStreetMap'
                }}).addTo(map);
                
                // Маркеры
                {map_js}
                
                // --- ФИЛЬТРАЦИЯ ---
                function applyFilters() {{
                    const region = document.getElementById('regionFilter').value;
                    const priceMax = parseFloat(document.getElementById('priceFilter').value) || Infinity;
                    const areaMin = parseFloat(document.getElementById('areaFilter').value) || 0;
                    const bargainOnly = document.getElementById('bargainFilter').checked;
                    
                    const rows = document.querySelectorAll('#offersBody tr');
                    let visibleCount = 0;
                    
                    rows.forEach(row => {{
                        const rowRegion = row.dataset.region || 'other';
                        const rowPrice = parseFloat(row.dataset.price) || 0;
                        const rowArea = parseFloat(row.dataset.area) || 0;
                        const isBargain = row.classList.contains('bargain-row');
                        
                        let visible = true;
                        if (region !== 'all' && rowRegion !== region) visible = false;
                        if (rowPrice > priceMax) visible = false;
                        if (rowArea < areaMin) visible = false;
                        if (bargainOnly && !isBargain) visible = false;
                        
                        row.classList.toggle('hidden', !visible);
                        if (visible) visibleCount++;
                    }});
                    
                    document.getElementById('totalCount').textContent = visibleCount;
                    document.getElementById('bargainCount').textContent = document.querySelectorAll('#offersBody tr.bargain-row:not(.hidden)').length;
                }}
                
                function resetFilters() {{
                    document.getElementById('regionFilter').value = 'all';
                    document.getElementById('priceFilter').value = '';
                    document.getElementById('areaFilter').value = '';
                    document.getElementById('bargainFilter').checked = false;
                    applyFilters();
                }}
                
                function sortTable(colIndex) {{
                    const tbody = document.getElementById('offersBody');
                    const rows = Array.from(tbody.querySelectorAll('tr:not(.hidden)'));
                    
                    rows.sort((a, b) => {{
                        const aVal = a.cells[colIndex]?.textContent?.trim() || '';
                        const bVal = b.cells[colIndex]?.textContent?.trim() || '';
                        
                        const aNum = parseFloat(aVal.replace(/[^\\d.-]/g, ''));
                        const bNum = parseFloat(bVal.replace(/[^\\d.-]/g, ''));
                        
                        if (!isNaN(aNum) && !isNaN(bNum)) {{
                            return aNum - bNum;
                        }}
                        return aVal.localeCompare(bVal);
                    }});
                    
                    rows.forEach(row => tbody.appendChild(row));
                }}
                
                // Применить фильтры при загрузке
                document.addEventListener('DOMContentLoaded', applyFilters);
            </script>
        </body>
        </html>
        """
        return html
    
    def save(self, offers: List[Dict], bargains: List[Dict]) -> str:
        """Сохраняет HTML-файл"""
        html_content = self.generate_html(offers, bargains)
        
        os.makedirs(os.path.dirname(OUTPUT["html_file"]), exist_ok=True)
        
        with open(OUTPUT["html_file"], "w", encoding="utf-8") as f:
            f.write(html_content)
        
        print(f"✅ HTML сохранён: {OUTPUT['html_file']}")
        return OUTPUT["html_file"]

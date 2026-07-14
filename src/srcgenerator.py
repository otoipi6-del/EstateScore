# src/generator.py

import os
from typing import List, Dict
from datetime import datetime

from config import OUTPUT


class HTMLGenerator:
    """Генерирует статический HTML-сайт с результатами"""
    
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
            
            is_bargain = offer.get("is_bargain", False)
            bargain_badge = (
                '<span class="badge bargain">🔥 Выгодный</span>' 
                if is_bargain else ''
            )
            
            row = f"""
            <tr class="{'bargain-row' if is_bargain else ''}">
                <td>{i}</td>
                <td><a href="{offer.get('url', '#')}" target="_blank">{offer.get('source', '')}</a></td>
                <td>{offer.get('address', '—')}</td>
                <td>{area_str} сот.</td>
                <td>{price_str} BYN</td>
                <td>{ppa_str} BYN/сот.</td>
                <td>{discount_str}</td>
                <td>{bargain_badge}</td>
            </tr>
            """
            rows.append(row)
        
        return "\n".join(rows)
    
    def generate_html(self, offers: List[Dict], bargains: List[Dict]) -> str:
        """Генерирует полный HTML-код"""
        
        current_time = datetime.now().strftime("%d.%m.%Y %H:%M")
        total_count = len(offers)
        bargain_count = len(bargains)
        
        table_rows = self.generate_table_rows(bargains)
        
        html = f"""
        <!DOCTYPE html>
        <html lang="ru">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>EstateScore — Мониторинг участков</title>
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
                    max-width: 1300px;
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
                .filter-info {{
                    background: white;
                    padding: 20px 30px;
                    border-radius: 12px;
                    margin-bottom: 30px;
                    box-shadow: 0 2px 8px rgba(0,0,0,0.06);
                    display: flex;
                    flex-wrap: wrap;
                    gap: 20px;
                    font-size: 14px;
                }}
                .filter-info .tag {{
                    background: #e9ecef;
                    padding: 4px 14px;
                    border-radius: 20px;
                    font-size: 13px;
                }}
                .filter-info .tag strong {{
                    color: #1a1a2e;
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
                @media (max-width: 768px) {{
                    body {{ padding: 15px; }}
                    .header {{ padding: 20px; flex-direction: column; gap: 15px; }}
                    .header .stats {{ gap: 15px; flex-wrap: wrap; justify-content: center; }}
                    .filter-info {{ flex-direction: column; gap: 8px; }}
                    th, td {{ padding: 8px 10px; font-size: 12px; }}
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
                            <span class="number">{total_count}</span>
                            Всего найдено
                        </div>
                        <div class="stat-item">
                            <span class="number">{bargain_count}</span>
                            Выгодных
                        </div>
                        <div class="stat-item">
                            <span class="number">{current_time}</span>
                            Обновлено
                        </div>
                    </div>
                </div>
                
                <!-- FILTER INFO -->
                <div class="filter-info">
                    <span><strong>📍 Регион:</strong> Минская область</span>
                    <span><strong>📐 Площадь:</strong> 10 соток</span>
                    <span><strong>🏷️ Тип:</strong> ИЖС</span>
                    <span><strong>⚡ Коммуникации:</strong> Газ, вода, электричество</span>
                    <span><strong>💰 Макс. цена за сотку:</strong> {ANALYSIS['max_price_per_are']} BYN</span>
                </div>
                
                <!-- TABLE -->
                <div class="table-wrapper">
                    <h3 style="margin-bottom: 16px; font-size: 18px;">🔥 Выгодные предложения</h3>
                    <table>
                        <thead>
                            <tr>
                                <th>#</th>
                                <th>Источник</th>
                                <th>Адрес</th>
                                <th>Площадь</th>
                                <th>Цена</th>
                                <th>Цена/сот.</th>
                                <th>Дискаунт</th>
                                <th>Статус</th>
                            </tr>
                        </thead>
                        <tbody>
                            {table_rows if table_rows else '<tr><td colspan="8" style="text-align:center; padding:30px;">😕 Выгодных предложений пока не найдено</td></tr>'}
                        </tbody>
                    </table>
                </div>
                
                <div class="footer">
                    EstateScore — автоматический мониторинг земельных участков в Минской области
                </div>
            </div>
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
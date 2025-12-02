import requests
from bs4 import BeautifulSoup
import pandas as pd
import time
import re

CITIES = {
    "台湾": ["Taipei"],
    "韓国": ["Seoul"],
    "マカオ": ["Macau"],
    "フィリピン": ["Manila"],
    "中国": ["Beijing", "Shanghai"],
    "香港": ["Hong-Kong"],
    "タイ": ["Bangkok", "Chiang-Mai"],
    "ベトナム": ["Ho-Chi-Minh-City", "Hanoi"],
    "マレーシア": ["Kuala-Lumpur"],
    "シンガポール": ["Singapore"],
    "日本": ["Osaka"]
}

def scrape_city(city_name):
    """都市のデータを取得"""
    url = f"https://www.numbeo.com/cost-of-living/in/{city_name}"
    headers = {'User-Agent': 'Mozilla/5.0'}

    response = requests.get(url, headers=headers, timeout=10)
    soup = BeautifulSoup(response.content, 'html.parser')
    
    items = {}
    tables = soup.find_all('table', class_='data_wide_table')

    for table in tables:
        for row in table.find_all('tr'):
            cols = row.find_all('td')
            if len(cols) >= 2:
                item_name = cols[0].get_text(strip=True)
                price_text = cols[1].get_text(strip=True)
                
                # 数値抽出
                price_match = re.search(r'[\d,]+\.?\d*', price_text)
                if price_match:
                    price = float(price_match.group().replace(',', ''))
                    items[item_name] = price
    
    
    return items

def main():
    all_data = []
    
    for country, cities in CITIES.items():
        print(f"{country}")
        for city in cities:
            print(f"  {city}...", end=" ")
            try:
                items = scrape_city(city)
                for item_name, price in items.items():
                    all_data.append({
                        'country': country,
                        'city': city,
                        'item': item_name,
                        'price': price
                    })
                print(f"{len(items)}項目")
                time.sleep(2)
            except Exception as e:
                print(f"エラー: {e}")
    
    # CSV保存
    df = pd.DataFrame(all_data)
    df.to_csv('numbeo_data.csv', index=False, encoding='utf-8-sig')
    print(f"\n保存完了: numbeo_data.csv ({len(df)}行)")

if __name__ == "__main__":
    main()
    
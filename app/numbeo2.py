import requests
from bs4 import BeautifulSoup
import pandas as pd
import time
import re

# 対象都市
CITIES = {
    "台湾": ["Taipei"],
    "韓国": ["Seoul"],
    "マカオ": ["Macao"],
    "フィリピン": ["Manila"],
    "中国": ["Beijing", "Shanghai"],
    "香港": ["Hong-Kong"],
    "タイ": ["Bangkok", "Chiang-Mai"],
    "ベトナム": ["Ho-Chi-Minh-City", "Hanoi"],
    "マレーシア": ["Kuala-Lumpur"],
    "シンガポール": ["Singapore"],
    "日本": ["Osaka"]
}

# カテゴリーマッピング（キーワードで分類）
CATEGORY_KEYWORDS = {
    "食費": [
        "meal", "restaurant", "mcmeal", "mcdonald"
    ],
    #"宿泊費": [    "hotel"],
    "交通費": [
        "taxi", "transport", "ticket", "pass"
    ]
}

def categorize_item(item_name):
    """項目名からカテゴリーを判定"""
    item_lower = item_name.lower()
    
    for category, keywords in CATEGORY_KEYWORDS.items():
        for keyword in keywords:
            if keyword in item_lower:
                return category
    
    return None  # カテゴリー不明

def scrape_city(city_name):
    """都市のデータを取得してカテゴリー別に集約"""
    url = f"https://www.numbeo.com/cost-of-living/in/{city_name}"
    headers = {'User-Agent': 'Mozilla/5.0'}
    
    response = requests.get(url, headers=headers, timeout=10)
    soup = BeautifulSoup(response.content, 'html.parser')
    
    # カテゴリー別の価格リスト
    categories = {
        "食費": [],
        "宿泊費": [],
        "交通費": []
    }
    
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
                    
                    # カテゴリー判定
                    category = categorize_item(item_name)
                    if category:
                        categories[category].append(price)
    
    # カテゴリーごとの平均を計算
    result = {}
    for category, prices in categories.items():
        if prices:
            result[category] = round(sum(prices) / len(prices), 2)
        else:
            result[category] = None
    
    return result

def main():
    all_data = []
    
    for country, cities in CITIES.items():
        print(f"{country}")
        for city in cities:
            print(f"  {city}...", end=" ")
            try:
                categories = scrape_city(city)
                
                data_row = {
                    'country': country,
                    'city': city,
                    '食費': categories['食費'],
                    #'宿泊費': categories['宿泊費'],
                    '交通費': categories['交通費']
                }
                all_data.append(data_row)
                
                print(f"食費:{categories['食費']}, 交通費:{categories['交通費']}")
                time.sleep(2)
            except Exception as e:
                print(f"エラー: {e}")
    
    # CSV保存
    df = pd.DataFrame(all_data)
    df.to_csv('numbeo_category_data.csv', index=False, encoding='utf-8-sig')
    print(f"\n保存完了: numbeo_category_data.csv ({len(df)}行)")

if __name__ == "__main__":
    main()
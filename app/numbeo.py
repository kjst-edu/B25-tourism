#%%
import requests
from bs4 import BeautifulSoup
import pandas as pd
import numpy as np
import time
from typing import Dict, Optional
import json

class NumbeoDataFetcher:
    """Numbeoからデータを取得するクラス"""
    
    BASE_URL = "https://www.numbeo.com/cost-of-living/in/"
    
    # 対象都市マッピング
    CITIES = {
        "中国": ["Beijing", "Shanghai", "Shenzhen", "Guangzhou"],
        "韓国": ["Seoul"],
        "台湾": ["Taipei"],
        "マカオ": ["Macau"],
        "香港": ["Hong-Kong"],
        "タイ": ["Bangkok", "Chiang-Mai", "Phuket"],
        "マレーシア": ["Kuala-Lumpur"],
        "シンガポール": ["Singapore"],
        "ベトナム": ["Ho-Chi-Minh-City", "Hanoi"],
        "日本": ["Osaka"]  # 基準都市
    }
#%%    
def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        })
    

def fetch_city_data(self, city_name: str) -> Optional[Dict]:
        """
        指定都市のデータを取得
        
        Args:
            city_name: 都市名（例: "Tokyo", "Seoul"）
        
        Returns:
            データ辞書 or None
        """
        try:
            url = f"{self.BASE_URL}{city_name}"
            response = self.session.get(url, timeout=10)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # データを抽出
            data = {
                'city': city_name,
                'items': {}
            }
            
            # 価格テーブルを探す
            tables = soup.find_all('table', {'class': 'data_wide_table'})
            
            for table in tables:
                rows = table.find_all('tr')
                for row in rows:
                    cols = row.find_all('td')
                    if len(cols) >= 2:
                        item_name = cols[0].get_text(strip=True)
                        price_text = cols[1].get_text(strip=True)
                        
                        # 価格を抽出（通貨記号を除去）
                        try:
                            price = float(price_text.replace(',', '').replace('¥', '').replace('$', '').split()[0])
                            data['items'][item_name] = price
                        except:
                            continue
        
            time.sleep(1)  # APIへの負荷を軽減
            return data
        except Exception as e:
            print(f"Error fetching {city_name}: {e}")
            return None

class CostOfLivingCalculator:
    """生活費指数を計算するクラス"""
    
    # 重み付け設定（旅行者向け）
    WEIGHTS = {
         
    }
 
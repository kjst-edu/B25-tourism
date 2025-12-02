
"""
為替レート取得プログラム（シンプル版）

必要なパッケージ:
pip install requests pandas
"""

import requests
import pandas as pd
from datetime import datetime

# 対象通貨
currencies = {
    '韓国ウォン': 'KRW',
    '台湾ドル': 'TWD',
    '香港ドル': 'HKD',
    'マカオパタカ': 'MOP',
    '中国人民元': 'CNY',
    'フィリピンペソ': 'PHP',
    'タイバーツ': 'THB',
    'ベトナムドン': 'VND',
    'マレーシアリンギット': 'MYR',
    'シンガポールドル': 'SGD'
}

def get_exchange_rates():
    """為替レートを取得"""
    url = "https://open.er-api.com/v6/latest/JPY"
    response = requests.get(url, timeout=10)
    rates_data = response.json()
    
    data = []
    rates = rates_data['rates']
    
    for country, code in currencies.items():
        jpy_to_currency = rates[code]
        currency_to_jpy = 1 / jpy_to_currency
        data.append([country, code, currency_to_jpy])
    
    return pd.DataFrame(data, columns=["通貨", "コード", "1単位あたりの円"])

if __name__ == "__main__":
    print(f"取得日時: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 50)
    
    df = get_exchange_rates()
    print(df.to_string(index=False))
    
    print("=" * 50)
    print(f"取得完了: {len(df)}通貨")
#Numbeoデータを日本円に換算するプログラム


import requests
import pandas as pd
from datetime import datetime

import os
#csv_path = "numbeo_category_data.csv"

# 国と通貨コードのマッピング
COUNTRY_CURRENCY_MAP = {
    '台湾': 'TWD',
    '韓国': 'KRW',
    'マカオ': 'MOP',
    'フィリピン': 'PHP',
    '中国': 'CNY',
    '香港': 'HKD',
    'タイ': 'THB',
    'ベトナム': 'VND',
    'マレーシア': 'MYR',
    'シンガポール': 'SGD',
    '日本': 'JPY'
}

def get_exchange_rates():
    """為替レートを取得"""
    url = "https://open.er-api.com/v6/latest/JPY"
    response = requests.get(url, timeout=10)
    rates_data = response.json()
    
    rates = {}
    for country, code in COUNTRY_CURRENCY_MAP.items():
        jpy_to_currency = rates_data['rates'][code]
        currency_to_jpy = 1 / jpy_to_currency
        rates[country] = currency_to_jpy
    
    return rates

def convert_to_jpy(csv_path):
    """CSVデータを円換算"""
    print(f"取得日時: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 70)
    
    # CSVを読み込み
    df = pd.read_csv(csv_path, encoding='utf-8-sig')
    print(f"CSVファイル読み込み: {len(df)}行")
    print(f"列: {list(df.columns)}")
    print()
    
    # 為替レート取得
    print("為替レート取得中...")
    rates = get_exchange_rates()
    print("為替レート取得完了")
    print()
    
    # 国ごとに為替レートを追加
    df['為替レート'] = df['country'].map(rates)
    
    # 各カテゴリーを円換算
    for column in ['食費', '交通費']:
        if column in df.columns:
            df[f'{column}_円'] = df[column] * df['為替レート']
        else:
            print(f"⚠️ 警告: '{column}' 列が見つかりません")
            print(f"   利用可能な列: {list(df.columns)}")
    
    # 結果を表示
    print("=" * 70)
    print("円換算結果")
    print("=" * 70)
    
    # 表示用に列を選択
    display_columns = ['country', 'city', '為替レート']
    for col in [ '食費_円', '交通費_円']:
        if col in df.columns:
            display_columns.append(col)
    
    print(df[display_columns].to_string(index=False))
    
    # CSVに保存
    output_path = csv_path.replace('.csv', '_jpy.csv')
    df.to_csv(output_path, index=False, encoding='utf-8-sig')
    print()
    print("=" * 70)
    print(f"保存完了: {output_path}")
    
    return df


convert_to_jpy("numbeo_category_data.csv")

# スクリプトの場所を基準にする（移植可能）
csv_path = os.path.join(os.path.dirname(__file__), "numbeo_category_data.csv")
#csv_path = "numbeo_category_data.csv"

# __file__ = スクリプト自身のパス（自動取得）
# これなら誰でもどこでも動く



"""
Numbeoデータを日本円に換算するプログラム

必要なパッケージ:
pip install requests pandas
"""

import requests
import pandas as pd
from datetime import datetime

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
    
    # ファイル情報を表示（デバッグ用）
    abs_path = os.path.abspath(csv_path)
    print(f"📂 読み込むファイル: {abs_path}")
    
    if os.path.exists(csv_path):
        mtime = datetime.fromtimestamp(os.path.getmtime(csv_path))
        print(f"📅 ファイル最終更新: {mtime.strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"📊 ファイルサイズ: {os.path.getsize(csv_path)} bytes")
    else:
        print(f"❌ ファイルが見つかりません: {csv_path}")
        return None
    
    print()
    
    # CSVを読み込み
    df = pd.read_csv(csv_path, encoding='utf-8-sig')
    print(f"CSVファイル読み込み: {len(df)}行")
    print(f"列: {list(df.columns)}")
    
    # 最初の3行を表示（データ確認）
    print("\n📋 読み込んだデータ（最初の3行）:")
    print(df.head(3))
    print()
    
    # 為替レート取得
    print("為替レート取得中...")
    rates = get_exchange_rates()
    print("為替レート取得完了")
    print()
    
    # 国ごとに為替レートを追加
    df['為替レート'] = df['country'].map(rates)
    
    # 各カテゴリーを円換算（食費と交通費のみ）
    for column in ['食費', '交通費']:
        if column in df.columns:
            df[f'{column}_円'] = df[column] * df['為替レート']
            print(f"✅ {column}_円 を計算しました")
        else:
            print(f"⚠️ 警告: '{column}' 列が見つかりません")
            print(f"   利用可能な列: {list(df.columns)}")
    
    print()
    
    # 結果を表示
    print("=" * 70)
    print("円換算結果")
    print("=" * 70)
    
    # 表示用に列を選択
    display_columns = ['country', 'city', '為替レート']
    for col in ['食費', '食費_円', '宿泊費', '宿泊費_円', '交通費', '交通費_円']:
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

if __name__ == "__main__":
    import os
    
    # 現在の作業ディレクトリを表示
    print(f"現在の作業ディレクトリ: {os.getcwd()}")
    print()
    
    # 同じフォルダ内のファイル一覧を表示
    print("このフォルダ内のファイル:")
    for file in os.listdir('.'):
        print(f"  - {file}")
    print()
    
    # 同じフォルダ内のCSVファイルを読み込み
    csv_path = "numbeo_category_data.csv"
    
    # ファイルの存在確認
    if os.path.exists(csv_path):
        print(f"✅ ファイル発見: {csv_path}")
        print(f"   絶対パス: {os.path.abspath(csv_path)}")
        print()
        df = convert_to_jpy(csv_path)
    else:
        print(f"❌ エラー: '{csv_path}' が見つかりません")
        print(f"   探している場所: {os.path.abspath(csv_path)}")
        print()
        print("対処方法:")
        print("1. 'numbeo_category_data.csv' をこのプログラムと同じフォルダに配置")
        print("2. またはターミナルでCSVファイルがあるフォルダに移動してから実行")

import os
import amadeus
from amadeus import Client, ResponseError

import pandas as pd
from datetime import datetime, timedelta

# Amadeus APIキーは環境変数から読み込む
API_KEY = os.environ.get("AMADEUS_API_KEY")
API_SECRET = os.environ.get("AMADEUS_API_SECRET")

# 目的地（国名: 空港コード）
DESTINATIONS = {
    "韓国": "ICN",           # ソウル・仁川
    "中国": "PEK",           # 北京
    "タイ": "BKK",           # バンコク
    "フィリピン": "MNL",      # マニラ
    "ベトナム": "SGN",        # ホーチミン
    "マカオ": "MFM",          # マカオ
    "香港": "HKG",           # 香港
    "台湾": "TPE",           # 台北
    "マレーシア": "KUL",      # クアラルンプール
    "シンガポール": "SIN"     # シンガポール
}

def search_flights(origin, destination, departure_date):
    """
    フライトを検索
    
    Args:
        origin: 出発空港コード
        destination: 到着空港コード
        departure_date: 出発日 (YYYY-MM-DD)
    
    Returns:
        list: フライト情報のリスト
    """
    if not API_KEY or not API_SECRET:
        raise RuntimeError("AMADEUS_API_KEY and AMADEUS_API_SECRET must be set")

    amadeus = Client(
        client_id=API_KEY,
        client_secret=API_SECRET
    )
    
    try:
        response = amadeus.shopping.flight_offers_search.get(
            originLocationCode=origin,
            destinationLocationCode=destination,
            departureDate=departure_date,
            adults=1,
            currencyCode='JPY',
            max=3  # 最大max件取得
        )
        
        flights = []
        for offer in response.data:
            # フライト情報を抽出
            itinerary = offer['itineraries'][0]
            segment = itinerary['segments'][0]
            
            flight_info = {
                '出発空港': segment['departure']['iataCode'],
                '到着空港': segment['arrival']['iataCode'],
                '出発時刻': segment['departure']['at'],
                '到着時刻': segment['arrival']['at'],
                '航空会社': segment['carrierCode'],
                '便名': segment['number'],
                '価格': offer['price']['total'],
                '通貨': offer['price']['currency']
            }
            flights.append(flight_info)
        
        return flights
    
    except ResponseError as error:
        print(f"エラー: {error}")
        return []

def format_datetime(dt_str):
    """日時を見やすくフォーマット"""
    dt = datetime.fromisoformat(dt_str.replace('Z', '+00:00'))
    return dt.strftime('%Y-%m-%d %H:%M')

def main():
    print("=" * 80)
    print("Amadeus フライト検索")
    print("出発: 関西国際空港 (KIX)")
    print("=" * 80)
    print()
    
    origin = "KIX"
    #departure_date = (datetime.now() + timedelta(days=30)).strftime("%Y-%m-%d")
    departure_date = (datetime.now() + timedelta(days=1)).strftime("%Y-%m-%d")
    
    print(f"出発日: {departure_date}")
    print()
    
    all_results = []
    
    for country, airport_code in DESTINATIONS.items():
        print(f"検索中: {country} ({airport_code})...")
        
        flights = search_flights(origin, airport_code, departure_date)
        
        if flights:
            print(f"  → {len(flights)}件のフライトを取得")
            for flight in flights:
                flight['国'] = country
                all_results.append(flight)
        else:
            print(f"  → フライトが見つかりませんでした")
        
        print()
    
    # 結果を表示
    if all_results:
        print("=" * 80)
        print("検索結果")
        print("=" * 80)
        print()
        
        for i, flight in enumerate(all_results, 1):
            print(f"{i}. {flight['国']} ({flight['到着空港']})")
            print(f"   出発: {format_datetime(flight['出発時刻'])}")
            print(f"   到着: {format_datetime(flight['到着時刻'])}")
            print(f"   航空会社: {flight['航空会社']} {flight['便名']}")
            print(f"   価格: ¥{flight['価格']}")
            print()
        
        # CSV保存
        df = pd.DataFrame(all_results)
        df['出発時刻'] = df['出発時刻'].apply(format_datetime)
        df['到着時刻'] = df['到着時刻'].apply(format_datetime)
        
        output_file = "amadeus_flights.csv"
        df.to_csv(output_file, index=False, encoding='utf-8-sig')
        
        print("=" * 80)
        print(f"CSV保存完了: {output_file}")
        print(f"取得件数: {len(all_results)}件")
        print("=" * 80)
    else:
        print("フライトが見つかりませんでした")

if __name__ == "__main__":
    main()

import requests
import json

host = 'flights-sky.p.rapidapi.com'

url = "https://flights-sky.p.rapidapi.com/web/flights/search-one-way"
headers = {
    "X-RapidAPI-Key": "0cf250c0a9msh4b6d63cf748e07fp1cb7bcjsn5d4fa8bde963",
    "X-RapidAPI-Host": "flights-sky.p.rapidapi.com"
}
params = {
    
  "placeIdFrom": "KIX",
  "placeIdTo": "ICN",
  "departDate": "2026-01-07",
  "currency": "JPY"


}

response = requests.get(url, headers=headers, params=params)
data = response.json()

import json

# data 変数にはAPIの結果が入っている前提

print(f"{'航空会社':<20} | {'価格':<10} | {'出発':<20} -> {'到着'}")
print("-" * 80)

# 1. データを取り出す
raw_itineraries = data['data']['itineraries']

# リストならそのまま、辞書なら values() をリスト化
if isinstance(raw_itineraries, dict):
    potential_flights = list(raw_itineraries.values())
else:
    potential_flights = raw_itineraries

# 2. ループ処理
count = 0
for flight in potential_flights:
    try:
        # ---【検問】ここが最重要ポイント ---
        # データが「辞書」でない、または「価格(price)」キーを持っていない場合は
        # フライト情報ではないとみなして無視（continue）する
        if not isinstance(flight, dict) or 'price' not in flight:
            continue
        # --------------------------------

        # 1. 価格取得
        price_info = flight.get('price', {})
        if isinstance(price_info, dict):
            price = price_info.get('formatted', '価格不明')
        else:
            price = str(price_info)

        # 2. フライト区間（legs）取得
        legs = flight.get('legs', [])
        if not legs:
            continue # legsがない場合もスキップ
            
        leg = legs[0]
        
        # 3. 航空会社取得
        carriers = leg.get('carriers', {})
        marketing = carriers.get('marketing', [])
        
        if marketing and isinstance(marketing, list) and len(marketing) > 0:
            airline_name = marketing[0].get('name', '不明な航空会社')
        else:
            # marketingがない場合のバックアップ
            operating = carriers.get('operating', [])
            airline_name = "航空会社不明"

        # 4. 時間取得
        dep_time = leg.get('departure', '').replace('T', ' ')
        arr_time = leg.get('arrival', '').replace('T', ' ')
        
        # 表示実行
        print(f"{airline_name:<20} | {price:<10} | {dep_time} -> {arr_time}")
        count += 1
        
    except Exception:
        # それでも何かエラーがあればスキップ
        continue

if count == 0:
    print("有効なフライトデータが見つかりませんでした。")
else:
    print("-" * 80)


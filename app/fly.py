
import requests
import json

def search_flights():
    # ---------------------------------------------------------
    # 1. 設定部分
    # ---------------------------------------------------------
    url = "https://flights-sky.p.rapidapi.com/web/flights/search-one-way"
    
    headers = {
        "X-RapidAPI-Key": "0cf250c0a9msh4b6d63cf748e07fp1cb7bcjsn5d4fa8bde963", # ★ここにキーを入れる
        "X-RapidAPI-Host": "flights-sky.p.rapidapi.com"
    }
    
    params = {
        "placeIdFrom": "KIX",      # 大阪（関空）
        "placeIdTo": "ICN",        # ソウル（仁川）
        "departDate": "2026-02-01",# 日付（未来の日付にしてください）
        "currency": "JPY"          # 日本円
    }

    print(f"検索中... ({params['placeIdFrom']} -> {params['placeIdTo']} : {params['departDate']})")

    try:
        # ---------------------------------------------------------
        # 2. データ取得
        # ---------------------------------------------------------
        response = requests.get(url, headers=headers, params=params)
        response.raise_for_status() # 通信エラーがあればここで止める
        data = response.json()
        
        print("データ取得成功。解析を開始します...\n")

        # ---------------------------------------------------------
        # 3. データの場所を探す（リストか辞書か自動判別）
        # ---------------------------------------------------------
        # データがない場合
        if 'data' not in data or 'itineraries' not in data['data']:
            print("エラー: フライト情報が見つかりませんでした。日付や空港コードを確認してください。")
            return

        raw_itineraries = data['data']['itineraries']
        
        # 辞書ならリストに変換、リストならそのまま
        if isinstance(raw_itineraries, dict):
            flights_list = list(raw_itineraries.values())
        elif isinstance(raw_itineraries, list):
            flights_list = raw_itineraries
        else:
            print("予期せぬデータ形式です。")
            return

        # ---------------------------------------------------------
        # 4. 表示処理（エラー防止の検問付き）
        # ---------------------------------------------------------
        print(f"{'航空会社':<20} | {'価格':<10} | {'出発時間':<20} -> {'到着時間'}")
        print("-" * 80)
        
        valid_count = 0
        
        for flight in flights_list:
            # 【検問1】 辞書型（ちゃんとしたデータ）以外は無視
            if not isinstance(flight, dict):
                continue
            
            # 【検問2】 価格情報がないデータ（広告など）は無視
            if 'price' not in flight:
                continue

            try:
                # --- 情報の抽出 ---
                
                # 価格
                price_info = flight['price']
                if isinstance(price_info, dict):
                    price = price_info.get('formatted', '不明')
                else:
                    price = str(price_info)

                # 足（区間情報）
                legs = flight.get('legs', [])
                if not legs: continue
                leg = legs[0]

                # 航空会社
                carriers = leg.get('carriers', {})
                marketing = carriers.get('marketing', [])
                if marketing and isinstance(marketing, list) and len(marketing) > 0:
                    airline = marketing[0].get('name', '不明')
                else:
                    airline = "不明"

                # 時間（Tをスペースに置換）
                dep = leg.get('departure', '').replace('T', ' ')
                arr = leg.get('arrival', '').replace('T', ' ')

                # 表示
                print(f"{airline:<20} | {price:<10} | {dep} -> {arr}")
                valid_count += 1

            except Exception:
                # 解析中に細かいエラーがあっても止まらない
                continue

        print("-" * 80)
        print(f"表示完了: {valid_count} 件のフライトが見つかりました。")

    except requests.exceptions.RequestException as e:
        print(f"通信エラーが発生しました: {e}")
    except json.JSONDecodeError:
        print("データの読み込みに失敗しました（JSON形式ではありません）。")

if __name__ == "__main__":
    search_flights()
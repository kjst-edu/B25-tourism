import time
import os
from datetime import datetime, timedelta
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager

# ==========================================
# 設定
# ==========================================
DESTINATIONS = {
    "Seoul": "ICN", 
    "Taipei": "TPE", 
    "Shanghai": "PVG", 
    "Hong Kong": "HKG", 
    "Bangkok": "BKK", 
    "Singapore": "SIN", 
    "Hanoi": "HAN", 
    "Ho Chi Minh City": "SGN"
}

def search_google_flights():
    tomorrow = datetime.now() + timedelta(days=1)
    date_str = tomorrow.strftime('%Y-%m-%d')
    
    print(f"🚀 {date_str} の直行便をGoogleフライトから取得します...")
    
    # スクリーンショット保存用のフォルダ作成
    if not os.path.exists("screenshots"):
        os.makedirs("screenshots")

    options = Options()
    # options.add_argument('--headless') # 動作確認中は画面を出したほうがいいです
    options.add_argument('--lang=ja-JP')
    options.add_argument('--window-size=1200,800') # 画面を少し大きくして見やすくする
    
    # ユーザーエージェント偽装（ロボットだと思われないようにする）
    options.add_argument('--user-agent=Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36')

    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)

    print(f"{'都市':<15} | {'価格':<10} | {'航空会社'}")
    print("-" * 50)

    for city_name, city_code in DESTINATIONS.items():
        try:
            # URL生成：直行便(s=0), 片道(tt=o), 1人(px=1)
            # q=Flights to {city_code} from KIX on {date_str}
            url = f"https://www.google.com/travel/flights?q=Flights%20to%20{city_code}%20from%20KIX%20on%20{date_str}%20oneway%20nonstop&hl=ja&curr=JPY"
            
            driver.get(url)
            
            # 読み込み待ち（長めに7秒）
            time.sleep(7)

            try:
                # 【作戦1】 「最安値」リストの一番上の価格を探す（汎用的なXpath）
                # 意味：liタグ（リスト）の中で、aria-labelが設定されているものを探す
                flights = driver.find_elements(By.XPATH, '//li[contains(@class, "pIav2d") or @role="listitem"]')
                
                # もしリストが見つからなければ、もっと広い条件で探す
                if not flights:
                    flights = driver.find_elements(By.XPATH, '//div[@role="main"]//li')

                found = False
                for flight in flights:
                    text = flight.text
                    # テキストの中に「円」が含まれていて、改行がある（＝情報が詰まっている）なら採用
                    if "円" in text and "\n" in text:
                        # テキストを行ごとに分割
                        lines = text.split('\n')
                        
                        # 価格を探す（"円"がついている行）
                        price = "不明"
                        airline = "不明"
                        
                        for line in lines:
                            if "円" in line and len(line) < 20: # 20文字以内の「円」は価格の可能性大
                                price = line
                                break
                        
                        # 航空会社はだいたい時間の近くにあることが多いが、簡易的に
                        # 「時間」を含まない、短い行を航空会社とみなすロジックなどが必要
                        # ここでは全テキストの1-2行目を採用してみる
                        airline = lines[1] if len(lines) > 1 else lines[0]

                        print(f"{city_name:<15} | {price:<10} | {airline[:10]}...") # 長すぎるのでカット
                        found = True
                        break # 最安値だけ欲しいのでループを抜ける
                
                if not found:
                    # 失敗時のスクショ
                    driver.save_screenshot(f"screenshots/fail_{city_name}.png")
                    print(f"{city_name:<15} | ---        | 直行便なし/解析不能 (スクショ保存)")

            except Exception as e:
                driver.save_screenshot(f"screenshots/error_{city_name}.png")
                print(f"{city_name:<15} | エラー      | {e}")

        except Exception as e:
            print(f"{city_name:<15} | 通信エラー   | {e}")

    print("-" * 50)
    driver.quit()

if __name__ == "__main__":
    search_google_flights()
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import datetime

# --- Chrome Headless 設定 ---
options = Options()
options.add_argument("--headless")
options.add_argument("--disable-gpu")
options.add_argument("--no-sandbox")
options.add_argument("--lang=ja-JP")  # 日本語表示

driver = webdriver.Chrome(options=options)

# 出発日（明日）
tomorrow = (datetime.date.today() + datetime.timedelta(days=1)).strftime("%Y%m%d")

# 出発地・目的地リスト
ORIGIN = "kix"
destinations = {
    "韓国（ソウル）": "icn",
    "台湾（台北）": "tpe",
    "香港": "hkg",
    "マカオ": "mfm",
    "中国（北京）": "pek",
    "フィリピン（マニラ）": "mnl",
    "タイ（バンコク）": "bkk",
    "ベトナム（ホーチミン）": "sgn",
    "マレーシア（クアラルンプール）": "kul",
    "シンガポール": "sin"
}

print(f"=== {tomorrow[:4]}-{tomorrow[4:6]}-{tomorrow[6:]} に {ORIGIN.upper()} から出発する便の最安値 ===\n")

for city, dest in destinations.items():
    url = f"https://www.skyscanner.jp/transport/flights/{ORIGIN}/{dest}/{tomorrow}/"
    driver.get(url)

    try:
        # ページ読み込み後に「¥」を含む最安値要素を待機
        price_element = WebDriverWait(driver, 15).until(
            EC.presence_of_element_located(
                (By.XPATH, "//span[contains(text(),'¥')]")
            )
        )
        price_text = price_element.text.strip()
        print(f"{city}: 最安 {price_text}")

    except Exception as e:
        print(f"{city}: 取得できませんでした ({e})")

driver.quit()

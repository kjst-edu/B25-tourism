from shiny import App, ui, render, reactive
import yfinance as yf
from datetime import datetime
import pandas as pd

# 通貨ペア
currency_pairs = {
    '韓国ウォン': 'KRWJPY=X',
    '台湾ドル': 'TWDJPY=X',
    '香港ドル': 'HKDJPY=X',
    'マカオパタカ': 'MOPJPY=X',
    '中国人民元': 'CNYJPY=X',
    'フィリピンペソ': 'PHPJPY=X',
    'タイバーツ': 'THBJPY=X',
    'ベトナムドン': 'VNDJPY=X',
    'マレーシアリンギット': 'MYRJPY=X',
    'シンガポールドル': 'SGDJPY=X'
}

def get_exchange_rates():
    data = []
    for country, ticker in currency_pairs.items():
        try:
            if country == 'マカオパタカ':
                hkd_rate = yf.Ticker('HKDJPY=X').history(period='1d')['Close'].iloc[-1]
                mop_to_hkd = 0.97
                latest_rate = hkd_rate * mop_to_hkd
                data.append([country, "MOP", f"{latest_rate:.4f}", "HKD換算"])
                continue

            hist = yf.Ticker(ticker).history(period='1d')
            if not hist.empty:
                latest_rate = hist['Close'].iloc[-1]
                data.append([country, ticker.replace('JPY=X', ''), f"{latest_rate:.4f}", ""])
            else:
                data.append([country, "-", "取得失敗", ""])
        except Exception as e:
            data.append([country, "-", f"エラー: {str(e)}", ""])
    return pd.DataFrame(data, columns=["通貨", "コード", "1単位あたりの円", "備考"])

# UI
app_ui = ui.page_fluid(
    ui.h2("東アジア通貨 為替レート（対JPY）"),
    ui.p("Yahoo! Finance から取得（更新ボタンで再取得）"),
    ui.input_action_button("refresh", "最新レートを取得"),
    ui.output_text("timestamp"),
    ui.output_table("rate_table"),
)

# Server
def server(input, output, session):
    # データをreactiveで管理
    rates_data = reactive.Value(get_exchange_rates())

    @reactive.Effect
    @reactive.event(input.refresh)
    def _():
        # ボタン押下時にデータ再取得
        rates_data.set(get_exchange_rates())

    @render.text
    def timestamp():
        return f"最終更新: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"

    @render.table
    def rate_table():
        return rates_data.get()

# アプリ起動
app = App(app_ui, server)

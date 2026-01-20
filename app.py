import pandas as pd
from shiny import App, render, ui, reactive
import os

# --- ファイルパスの設定 ---
# あなたの環境に合わせて絶対パスで指定します
FLIGHT_PATH = "amadeus_flights.csv"
COST_PATH = "numbeo_category_data_jpy.csv"

def load_data():
    if not os.path.exists(FLIGHT_PATH) or not os.path.exists(COST_PATH):
        print(f"⚠️ ファイルが見つかりません:\n航空券: {os.path.exists(FLIGHT_PATH)}\n物価: {os.path.exists(COST_PATH)}")
        return None

    # CSVの読み込み
    df_f = pd.read_csv(FLIGHT_PATH)
    df_c = pd.read_csv(COST_PATH)
    
    # マージ（amadeus_flights.csvの「国」とnumbeo_category_data_jpy.csvの「country」を結合）
    merged = pd.merge(df_f, df_c, left_on="国", right_on="country", how="inner")
    
    # 重複する国名を整理し、価格を数値型に変換
    merged['価格'] = pd.to_numeric(merged['価格'], errors='coerce')
    
    print(f"✅ データを統合しました: {len(merged)}件ヒット")
    return merged

df_master = load_data()

# --- UIデザイン ---
app_ui = ui.page_fluid(
    ui.panel_title("✈️ アジア旅行 予算シミュレーター (KIX発)"),
    ui.markdown("---"),
    
    ui.layout_sidebar(
        ui.sidebar(
            ui.h4("プラン設定"),
            ui.input_slider("days", "滞在日数", 1, 10, 3),
            ui.input_numeric("budget", "総予算の上限 (円)", 150000, step=5000),
            
            ui.hr(),
            ui.h5("スタイル調整"),
            ui.input_slider("food_style", "食費（1.0=標準, 2.0=贅沢）", 0.5, 3.0, 1.0, step=0.1),
            ui.input_slider("trans_style", "移動（1.0=標準, 2.0=タクシー多）", 0.5, 3.0, 1.0, step=0.1),
            
            ui.hr(),
            ui.markdown("航空券データ: Amadeus API\n物価データ: Numbeo")
        ),
        
        ui.navset_card_pill(
            ui.nav_panel("おすすめの旅行先", 
                ui.output_ui("result_list")
            ),
            ui.nav_panel("詳細データ一覧", 
                ui.output_table("summary_table")
            )
        )
    )
)

# --- サーバーロジック ---
def server(input, output, session):
    
    @reactive.calc
    def filtered_df():
        if df_master is None or df_master.empty:
            return None
        
        df = df_master.copy()
        
        # 動的な計算
        df['calc_food'] = df['食費_円'] * input.food_style() * input.days()
        df['calc_trans'] = df['交通費_円'] * input.trans_style() * input.days()
        df['total_cost'] = df['価格'] + df['calc_food'] + df['calc_trans']
        
        # 予算フィルターと安い順ソート
        res = df[df['total_cost'] <= input.budget()].sort_values('total_cost')
        return res

    @render.ui
    def result_list():
        data = filtered_df()
        if data is None:
            return ui.markdown("### ⚠️ データファイルが読み込めませんでした。パスを確認してください。")
        if data.empty:
            return ui.markdown("### 該当なし\n予算を増やすか、日数を減らしてみてください。")

        cards = []
        for _, row in data.iterrows():
            cards.append(
                ui.card(
                    ui.card_header(ui.h4(f"{row['国']} ({row['city']})")),
                    ui.layout_column_wrap(
                        ui.div(
                            ui.h2(f"¥{int(row['total_cost']):,d}", style="color: #2c3e50;"),
                            ui.p(f"✈️ 航空券: ¥{int(row['価格']):,d}"),
                        ),
                        ui.div(
                            ui.p(f"📅 出発: {row['出発時刻']}"),
                            ui.p(f"🍴 食費計: ¥{int(row['calc_food']):,d}"),
                            ui.p(f"🚗 交通費計: ¥{int(row['calc_trans']):,d}"),
                        ),
                        width=1/2
                    ),
                    style="margin-bottom: 15px; border-left: 10px solid #3498db;"
                )
            )
        return ui.div(*cards)

    @render.table
    def summary_table():
        data = filtered_df()
        if data is None: return None
        return data[['国', 'city', '価格', 'total_cost']].rename(
            columns={'価格': '航空券代', 'total_cost': '合計予算（円）'}
        )

app = App(app_ui, server)
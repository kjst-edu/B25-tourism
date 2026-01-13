import pandas as pd
from shiny import App, render, ui, reactive
import os

# --- データの読み込み ---
def load_data():
    flight_file = "amadeus_flights.csv"
    cost_file = "numbeo_category_data_jpy.csv"
    
    if not os.path.exists(flight_file) or not os.path.exists(cost_file):
        return None

    # Amadeus APIから取得した航空券データ
    df_f = pd.read_csv(flight_file)
    # Numbeoから取得し円換算した物価データ
    df_c = pd.read_csv(cost_file)
    
    # 結合して一つのデータフレームにする
    return pd.merge(df_f, df_c, left_on="国", right_on="country", how="inner")

df_master = load_data()

# --- UIデザイン ---
app_ui = ui.page_fluid(
    ui.panel_title("📊 アジア旅行・動的予算シミュレーター"),
    
    ui.layout_sidebar(
        ui.sidebar(
            ui.h4("旅行プラン設定"),
            ui.input_slider("days", "滞在日数", 1, 14, 3),
            ui.input_numeric("budget", "予算上限 (円)", 120000, step=5000),
            
            ui.hr(),
            ui.h5("スタイル調整"),
            # 係数をかけて動的に物価を変動させる
            ui.input_slider("food_style", "食費レベル (0.5=節約, 2.0=贅沢)", 0.5, 2.0, 1.0, step=0.1),
            ui.input_slider("trans_style", "移動レベル (タクシー多めなど)", 0.5, 2.0, 1.0, step=0.1),
            
            ui.hr(),
            ui.markdown("※航空券はAmadeus APIの最新値")
        ),
        
        ui.navset_tab(
            ui.nav_panel("予算内ランキング", 
                ui.output_ui("result_list")
            ),
            ui.nav_panel("費用内訳データ", 
                ui.output_table("summary_table")
            )
        )
    )
)

# --- サーバーロジック ---
def server(input, output, session):
    
    # --- リアクティブ計算: 入力が変わるたびに自動計算される ---
    @reactive.calc
    def calc_total_costs():
        if df_master is None:
            return None
        
        df = df_master.copy()
        
        # 動的な計算ロジック
        # 合計 = 航空券代 + (食費 * スタイル * 日数) + (交通費 * スタイル * 日数)
        df['calc_food'] = df['食費_円'] * input.food_style() * input.days()
        df['calc_trans'] = df['交通費_円'] * input.trans_style() * input.days()
        df['total_cost'] = df['価格'] + df['calc_food'] + df['calc_trans']
        
        # 予算内でフィルタリング
        return df[df['total_cost'] <= input.budget()].sort_values('total_cost')

    # --- 結果の表示 (カード形式) ---
    @render.ui
    def result_list():
        data = calc_total_costs()
        if data is None or data.empty:
            return ui.div(ui.h3("該当なし"), ui.p("予算を増やすか、スタイルを『節約』にしてみてください。"))

        cards = []
        for _, row in data.iterrows():
            cards.append(
                ui.card(
                    ui.card_header(f"{row['国']} ({row['city']})"),
                    ui.layout_column_wrap(
                        ui.div(
                            ui.h3(f"総額: ¥{int(row['total_cost']):,d}"),
                            ui.p(f"✈️ 航空券: ¥{int(row['価格']):,d}", style="color: blue;"),
                        ),
                        ui.div(
                            ui.p(f"🍴 食費計: ¥{int(row['calc_food']):,d}"),
                            ui.p(f"🚗 交通費計: ¥{int(row['calc_trans']):,d}"),
                            ui.p(f"1日あたりの現地費: ¥{int((row['calc_food']+row['calc_trans'])/input.days()):,d}")
                        ),
                        width=1/2
                    ),
                    style="margin-bottom: 15px; border-left: 8px solid #0d6efd;"
                )
            )
        return ui.div(*cards)

    # --- 数値一覧の表示 ---
    @render.table
    def summary_table():
        data = calc_total_costs()
        if data is None: return None
        return data[['国', 'city', '価格', 'total_cost']].rename(columns={'価格': '航空券代', 'total_cost': '合計費用'})

app = App(app_ui, server)

import pandas as pd
import plotly.express as px
from shinywidgets import output_widget, render_widget
from shiny import App, render, ui

app_ui = ui.page_fluid(
    ui.panel_title("Good flight"),
    ui.input_slider("n", "N", 0, 100, 20),
    ui.output_text_verbatim("txt"),
    output_widget("numbeo_plot"),
    output_widget("flight_plot")
)


def server(input, output, session):
    @render.text
    def txt():
        return f"n*2 is {input.n() * 2}"


    @render_widget
    def numbeo_plot():
        df = pd.read_csv("numbeo_category_data_jpy.csv") 
        df['合計_円'] = df['食費_円'] + df['交通費_円']
        df_sorted = df.sort_values("合計_円", ascending=True) # ソート
    
    
        fig = px.bar(df_sorted, x=["食費_円", "交通費_円"], y="country", orientation='h', text_auto=True)
    
        return fig  
    
    def flight_plot():
        df = pd.read_csv("amadeus_search.csv")
        df_sorted = df.sort_values("価格", ascending=True)
        fig = px.bar(df_sorted, x="価格", y="国", orientation='h', text_auto=True)
        return fig

app = App(app_ui, server)
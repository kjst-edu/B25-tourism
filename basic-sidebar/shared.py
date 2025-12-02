from pathlib import Path

import pandas as pd



app_dir = Path(__file__).parent
root_B25TOURISM = app_dir.parent
input_csv = root_B25TOURISM / "app" / "numbeo_category_data_jpy.csv"
df = pd.read_csv("numbeo_category_data_jpy.csv")

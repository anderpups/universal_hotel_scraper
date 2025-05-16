import glob
import json
import os
import pandas

data_folder = "data"
all_data = []

# Find all JSON files in the data folder
json_files = glob.glob(os.path.join(data_folder, "*.json"))

for file_path in json_files:
    with open(file_path, "r") as f:
        data = json.load(f)
        gather_date = os.path.basename(file_path).split("-")[1].split(".")[0]
    df = pandas.DataFrame(data)

    pivot_df = df.pivot_table(index='date', columns='name', values='price')
    
    pivot_df.to_html(f"{data_folder}/hotel_info-{gather_date}.html")
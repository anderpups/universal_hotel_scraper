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
        all_data.extend(data)

print(f"Loaded {len(all_data)} records from {len(json_files)} files.")

dataframe = pandas.DataFrame(all_data)

dataframe.groupby(['date'])

print(dataframe.first())
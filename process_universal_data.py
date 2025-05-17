import glob
import json
import os
import pandas

data_folder = "data"
all_data = []

# Find all JSON files in the data folder
json_files = glob.glob(os.path.join(data_folder, "hotel_info*.json"))

def format_price(price):
    """Format the price to include a dollar sign """
    try:
        return f"${int(price)}"
    except ValueError:
        return "N/A"

# def set_highlight(cell):
#     isna = True if cell == 'N/A' else False
#     return ['background-color: LightGray' if isna else '']

for file_path in json_files:
    with open(file_path, "r") as f:
        data = json.load(f)
        gather_date = os.path.basename(file_path).split("-")[1].split(".")[0]
    df = pandas.DataFrame(data)
    pivot_df = df.pivot_table(index='date', columns='name', values='price')
    
    pivot_df.index = pandas.to_datetime(pivot_df.index, format='%m/%d/%y')
    pivot_df = pivot_df.sort_index()

    ## Format the price columns
    for col in pivot_df.columns:
        pivot_df[col] = pivot_df[col].apply(format_price)
    
    with open(f'{data_folder}/crowd_info-{gather_date}.json', "r") as f:
        crowd_info = json.load(f)
    crowd_info_series = pandas.Series(
        [item['crowd_info'] for item in crowd_info],
        index=[item['date'] for item in crowd_info]
    )
    crowd_info_series.index = pandas.to_datetime(crowd_info_series.index, format='%m/%d/%y')
    ## Add the crowd info to the pivot_df
    pivot_df.insert(0, 'Crowd', crowd_info_series)

    # pivot_df['crowd_info'] = crowd_info_series
    ## Get the Day from the date and add it to the pivot_df
    day = pandas.to_datetime(pivot_df.index, format='%m/%d/%y').strftime('%a')
    pivot_df.insert(0, 'Day', day)
    pivot_df.index = pandas.to_datetime(pivot_df.index, format='%m/%d/%y').strftime('%m/%d/%y')
    pivot_df.to_html(f"{data_folder}/hotel_info-{gather_date}.md", index_names=False)
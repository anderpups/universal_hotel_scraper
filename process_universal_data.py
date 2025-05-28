import glob
import json
import os
import time
import pprint
import pandas
import matplotlib
import matplotlib.pyplot as plt
from itertools import groupby
from datetime import datetime
from jinja2 import Environment, FileSystemLoader

data_folder = "data"
index_html_file_path = os.path.join(data_folder, "index.html")
historical_info_html_file_path = os.path.join(data_folder, "historical_info.html")
environment = Environment(loader=FileSystemLoader("templates/"))
hotel_info_template = environment.get_template("hotel-info.html.j2")
index_template = environment.get_template("index.html.j2")
index_html_by_gather_date = '<h2>Info by Gather Date</h2>'
index_html_by_hotel = '<h2>Info by Hotel</h2>'
historical_html_by_gather_date = '<link rel="stylesheet" href="style.css">\n<h2>Historical Info by Gather Date</h2>'

all_data = []
info_by_hotel = []

def format_price(price):
    """Format the price to include a dollar sign """
    try:
        return int(price)
    except ValueError:
        return "unavailable"

def color_gradient(s, color_list=['#00ff00', '#ffff00', '#ff0000']):
    """
    Applies a smooth color gradient to a Pandas Series,
    using matplotlib for more colors between the ends.
    color_list: list of hex colors for the gradient stops.
    """
    max_val = s.max()
    min_val = s.min()
    if max_val == min_val:
        normalized = pandas.Series([0.5] * len(s), index=s.index)
    else:
        normalized = (s - min_val) / (max_val - min_val)

    cmap = matplotlib.colors.LinearSegmentedColormap.from_list("custom_gradient", color_list)

    def get_color(val):
        if pandas.isna(val):
            return 'background-color: DarkGray'
        r, g, b, _ = [int(x * 255) for x in cmap(val)]
        return f'background-color: rgb({r},{g},{b})'

    return normalized.apply(get_color)

## Find all JSON files in the data folder
json_files = glob.glob(os.path.join(data_folder, "hotel_info*.json"))
json_files.sort(reverse=True)
info_by_gather_date = {}

## Loop through json files
for index, file_path in enumerate(json_files):
    with open(file_path, "r") as f:
        data = json.load(f)
    filename = os.path.basename(file_path)
    gather_date = filename.split("-")[1].split(".")[0]
    for info in data:
        if info_by_gather_date.get(info['name']) is None:
            info_by_gather_date[info['name']] = []
        info_by_gather_date[info['name']] = info_by_gather_date[info['name']] + [{"date": info['date'], "price": info['price'], "gather_date": gather_date}]

    df = pandas.DataFrame(data)
    pivot_df = df.pivot_table(index='date', columns='name', values='price')
    
    pivot_df.index = pandas.to_datetime(pivot_df.index, format='%m/%d/%y')
    pivot_df = pivot_df.sort_index()
    
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
    
    ## Format the index to be the date in the format of mm/dd/yy
    pivot_df.index = pandas.to_datetime(pivot_df.index, format='%m/%d/%y').strftime('%m/%d/%y')

    # Apply color gradient and format each cell that is a price
    for col in pivot_df.columns:
        if col not in ['Day', 'Crowd']:
            styles = color_gradient(pivot_df[col])
            pivot_df[col] = [
                f'<div style="{style}">{format_price(val)}</div>'
                for style, val in zip(styles, pivot_df[col])
            ]

    # Setting gradient color for the 'Crowd' column
    styles = color_gradient(pivot_df['Crowd'])
    pivot_df['Crowd'] = [
        f'<div style="{style}">{val}</div>'
        for style, val in zip(styles, pivot_df['Crowd'])
    ]

    ## Remove the index and columns names
    pivot_df.index.name = None
    pivot_df.columns.name = None

    # styled_table = pivot_df.style.set_sticky(axis="columns")
    styled_table = pivot_df.style.set_table_styles([
        {'selector': 'th', 'props':
        [('background-color', 'white'),
        ('z-index', '10'),
        ('position', 'sticky !important'),
        ('top','50px')
        ]}
    ], overwrite=False)
    number_of_columns = (len(pivot_df.columns)+ 1)

    table_html = styled_table.to_html(uuid="hotel-info")

    total_html = hotel_info_template.render(
        table_html=table_html,
        number_of_columns=number_of_columns,
        format_start_column=3,
        by_hotel_html = False
        )

    with open(f"{data_folder}/hotel_info-{gather_date}.html", "w") as f:
        f.write(total_html) 

    if index < 10:
        index_html_by_gather_date += f'<a href="hotel_info-{gather_date}.html">{datetime.strptime(gather_date, "%Y%m%d").strftime("%m/%d/%Y ")}</a><br>\n'
    elif index == 11:
      index_html_by_gather_date += f'<a href="historical_info.html">Historical Info</a><br>\n'
    else:
        historical_html_by_gather_date += f'<a href="hotel_info-{gather_date}.html">{datetime.strptime(gather_date, "%Y%m%d").strftime("%m/%d/%Y ")}</a><br>\n'

for name, data in info_by_gather_date.items():

    df = pandas.DataFrame(data)
    pivot_df = df.pivot_table(index='date', columns='gather_date', values='price')
    number_of_columns = (len(pivot_df.columns)+ 1)
    # Apply color gradient and format each cell that is a price
    for col in pivot_df.columns:
        styles = color_gradient(pivot_df[col])
        pivot_df[col] = [
            f'<div style="{style}">{format_price(val)}</div>'
            for style, val in zip(styles, pivot_df[col])
        ]
    # Format the index to be the date in the format of mm/dd/yy
    pivot_df.columns = pandas.to_datetime(pivot_df.columns, format='%Y%m%d').strftime('%m/%d/%y')
    pivot_df = pivot_df.sort_index()

    ## Remove the index and columns names
    pivot_df.index.name = None
    pivot_df.columns.name = None

    styled_table = pivot_df.style.set_sticky(axis="columns")
    styled_table = pivot_df.style.set_table_styles([
        {'selector': 'th', 'props':
        [('background-color', 'white'),
        ('z-index', '10'),
        ('position', 'sticky !important'),
        ('top','50px')
        ]}
    ], overwrite=False)

    table_html = styled_table.to_html(uuid="hotel-info")
    
    total_html = hotel_info_template.render(
        table_html=table_html,
        number_of_columns=number_of_columns,
        format_start_column=1,
        by_hotel_html = True
        )

    with open(f'{data_folder}/hotel_info-{(name.replace(" ","_")).lower()}.html', "w") as f:
        f.write(total_html) 

    index_html_by_hotel += f'<a href="hotel_info-{(name.replace(" ","_")).lower()}.html">{name}</a><br>\n'

index_html = index_template.render(
    index_html_by_gather_date=index_html_by_gather_date,
    index_html_by_hotel=index_html_by_hotel
    )

# Write to index.html
with open(index_html_file_path, "w") as f:
    f.write(index_html)

# Write to historical file.html
with open(historical_info_html_file_path, "w") as f:
    f.write(historical_html_by_gather_date)

with open(f"{data_folder}/info_by_gather_date.json", "w") as file:
  json.dump(info_by_gather_date, file, indent=2)

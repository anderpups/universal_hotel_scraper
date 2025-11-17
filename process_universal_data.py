import glob
import json
import os
import time
import pprint
import pandas
import matplotlib
import matplotlib.pyplot as plt
from itertools import groupby
from datetime import datetime, timedelta
from jinja2 import Environment, FileSystemLoader

next_trip_date = 'Dec 12, 2025 20:00:00'

html_folder = 'html'
data_folder = f'{html_folder}/data'
index_html_file_path = os.path.join(html_folder, "index.html")
historical_info_html_file_path = os.path.join(html_folder, "historical_info.html")
environment = Environment(loader=FileSystemLoader("templates/"))
hotel_info_template = environment.get_template("hotel-info.html.j2")
index_template = environment.get_template("index.html.j2")
index_html_by_gather_date = '<h2><center>Info by Gather Date</center></h2>\n'
index_html_by_hotel = '<h2><center>Info by Hotel</center></h2>\n'
historical_html_by_gather_date = '<link rel="stylesheet" href="style.css">\n<div class="list-section">\n<h2><center>Historical Info by Gather Date</center></h2>\n'
data_html = '<link rel="stylesheet" href="style.css">\n<h2>JSON Data</h2>'

## Get todday
today = datetime.now()

## Get tomorrow
tomorrow = today + timedelta(days=1)

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
hotel_info_json_files = glob.glob(os.path.join(data_folder, "hotel_info*.json"))
hotel_info_json_files.sort(reverse=True)
info_by_gather_date = {}

## Loop through hotel info json files
for index, file_path in enumerate(hotel_info_json_files):
    with open(file_path, "r") as f:
        data = json.load(f)
    filename = os.path.basename(file_path)
    gather_date = filename.split("-")[1].split(".")[0]
    def add_suffix(day):
        """Adds the appropriate ordinal suffix to a day number."""
        # Check for the exceptions: 11th, 12th, 13th
        if 11 <= day % 100 <= 13:
            suffix = 'th'
        # Use .get() with a default 'th' to avoid index errors
        else:
            suffix = {1: 'st', 2: 'nd', 3: 'rd'}.get(day % 10, 'th')
        return f"{day}{suffix}"

    # ... rest of your code ...
    input_format = "%Y%m%d"
    date_obj = datetime.strptime(gather_date, input_format)

    formatted_date = f"{date_obj.strftime('%b')} {add_suffix(date_obj.day)}, {date_obj.strftime('%Y')}"
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
    ## Format the crowd info series index to be datetime
    crowd_info_series.index = pandas.to_datetime(crowd_info_series.index, format='%m/%d/%y')
    ## Add the crowd info to the pivot_df
    pivot_df.insert(0, 'Crowd', crowd_info_series)

    ## Get the Day from the date and add it to the pivot_df
    day = pandas.to_datetime(pivot_df.index, format='%m/%d/%y').strftime('%a')
    
    pivot_df.insert(0, 'Day', day)
    
    ## Format the index to be the date in the format of mm/dd/yy
    pivot_df.index = pandas.to_datetime(pivot_df.index, format='%m/%d/%y').strftime('%m/%d/%y')

    ## Apply color gradient and format each cell that is a price
    for col in pivot_df.columns:
        if col not in ['Day', 'Crowd']:
            styles = color_gradient(pivot_df[col])
            pivot_df[col] = [
                f'<div style="{style}">{format_price(val)}</div>'
                for style, val in zip(styles, pivot_df[col])
            ]

    ## Apply gradient color for the 'Crowd' column
    styles = color_gradient(pivot_df['Crowd'])
    pivot_df['Crowd'] = [
        f'<div style="{style}">{val}</div>'
        for style, val in zip(styles, pivot_df['Crowd'])
    ]

    ## Remove the index and columns names
    pivot_df.index.name = None
    pivot_df.columns.name = None

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
        gather_date=gather_date,
        formatted_date=formatted_date,
        by_hotel_html = False
        )

    with open(f"{html_folder}/hotel_info-{gather_date}.html", "w") as f:
        f.write(total_html)
    print(f"Generated HTML for gather date {formatted_date}")
    print(f"Dates left to process: {len(hotel_info_json_files) - index - 1}")

    if index < 10:
        index_html_by_gather_date += f'<a href="hotel_info-{gather_date}.html">{datetime.strptime(gather_date, "%Y%m%d").strftime("%m/%d/%Y ")}</a>\n'
    elif index == 11:
      index_html_by_gather_date += f'<a href="historical_info.html">Historical Info</a>\n'
    else:
        historical_html_by_gather_date += f'<a href="hotel_info-{gather_date}.html">{datetime.strptime(gather_date, "%Y%m%d").strftime("%m/%d/%Y ")}</a>\n'

# Sort dictionary by hotel name
info_by_gather_date = {k:v for k,v in sorted(info_by_gather_date.items(), key=lambda item: item[0])}

## Loop through the info_by_gather_date dictionary to create individual hotel info pages
for name, data in info_by_gather_date.items():

    ## Create DataFrame and pivot table
    df = pandas.DataFrame(data)
    pivot_df = df.pivot_table(index='date', columns='gather_date', values='price')
    
    ## Get number of columns for the table
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
    pivot_df = pivot_df.sort_index(axis=1, ascending=False)

    ## Remove the index and columns names
    pivot_df.index.name = None
    pivot_df.columns.name = None
    
    ## Set style of table
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
        tomorrow = tomorrow.strftime("%Y-%m-%d"),
        by_hotel_html = True,
        name=name
        )

    with open(f'{html_folder}/hotel_info-{(name.replace(" ","_")).lower()}.html', "w") as f:
        f.write(total_html) 
    print(f"Generated HTML for {name}")
    index_html_by_hotel += f'<a href="hotel_info-{(name.replace(" ","_")).lower()}.html">{name}</a>\n'

index_html = index_template.render(
    index_html_by_gather_date=index_html_by_gather_date,
    index_html_by_hotel=index_html_by_hotel,
    next_trip_date=next_trip_date
    )

# Write to index.html
with open(index_html_file_path, "w") as f:
    f.write(index_html)

# Write to historical file.html
with open(historical_info_html_file_path, "w") as f:
    f.write(historical_html_by_gather_date)

data_location_list = ''

with open(f"{data_folder}/info_by_gather_date.json", "w") as file:
  json.dump(info_by_gather_date, file, indent=2)
all_json_files = glob.glob(os.path.join(data_folder, "*.json"))
all_json_files = sorted(all_json_files)
for json_file in all_json_files:
    data_html += f'<a href="{os.path.basename(json_file)}">{os.path.basename(json_file)}</a><br>\n'
    data_location_list += f'https://anderpups.github.io/data/{os.path.basename(json_file)}\n'

with open(f'{data_folder}/index.html', "w") as f:
    f.write(data_html)

with open(f'{data_folder}/data_location_list.txt', "w") as f:
    f.write(data_location_list)

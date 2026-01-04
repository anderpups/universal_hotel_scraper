import glob
import json
import os
import time
from itertools import groupby
from datetime import datetime, timedelta
from jinja2 import Environment, FileSystemLoader
from zoneinfo import ZoneInfo

next_trip_date = 'Jan 09, 2026 09:00:00'

html_folder = 'html'
data_folder = f'{html_folder}/data'
index_html_file_path = os.path.join(html_folder, "index.html")
environment = Environment(loader=FileSystemLoader("templates/"))
hotel_prices_template = environment.get_template("hotel_prices.html.j2")
hotel_prices_html_file_path = os.path.join(html_folder, "hotel_prices.html")
index_template = environment.get_template("index.html.j2")
chart_html_file = os.path.join(html_folder, "price_chart.html")

## Get todday
today = datetime.now(ZoneInfo("America/New_York"))

## Get tomorrow
tomorrow = today + timedelta(days=1)

hotel_prices_html = hotel_prices_template.render(
    today_date=today.strftime('%Y-%m-%d'),
    today_date_text=today.strftime('%B %-d, %Y')
    )

with open(hotel_prices_html_file_path, "w") as f:
    f.write(hotel_prices_html)

data_location_list = ''

all_json_files = glob.glob(os.path.join(data_folder, "*.json"))
all_json_files = sorted(all_json_files)
for json_file in all_json_files:
    data_location_list += f'https://anderpups.github.io/data/{os.path.basename(json_file)}\n'

with open(f'{data_folder}/data_location_list.txt', "w") as f:
    f.write(data_location_list)

# Generate price chart page

chart_template = environment.get_template("price-chart.html.j2")

# Find all JSON files (Updated for new naming convention)
# Expected format: hotel-prices-20250514.json
hotel_prices_json_files = glob.glob(os.path.join(data_folder, "hotel-prices-*.json"))
hotel_prices_json_files.sort()

# Build a list of available data files to pass to JavaScript
data_files = []

for file_path in hotel_prices_json_files:
    filename = os.path.basename(file_path)
    # Filename format expected: hotel-prices-20250514.json
    # Split by '-' gives ['hotel', 'prices', '20250514.json']
    try:
        date_part = filename.split("-")[2].split(".")[0]
        gather_date = datetime.strptime(date_part, "%Y%m%d")
                
        data_files.append({
            'url': f"data/{filename}",
            'date': gather_date.strftime('%Y-%m-%d'),
            'id': date_part
        })
    except (IndexError, ValueError) as e:
        print(f"Skipping malformed filename {filename}: {e}")
        continue

print(f"Found {len(data_files)} valid data files to link.")

# Render the template with the list of files
html_content = chart_template.render(
    data_files=data_files,
    today=today.strftime('%Y-%m-%d')
)

# Write the HTML file
with open(chart_html_file, "w") as f:
    f.write(html_content)
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

## Get todday
today = datetime.now(ZoneInfo("America/New_York"))
print(f"Today's date: {today.strftime('%Y-%m-%d')}")
## Get tomorrow
tomorrow = today + timedelta(days=1)
end_date = today + timedelta(days=365)


index_html = index_template.render(
    next_trip_date=next_trip_date
    )

# Write to index.html
with open(index_html_file_path, "w") as f:
    f.write(index_html)

hotel_prices_html = hotel_prices_template.render(
    today_date=today.strftime('%Y-%m-%d'),
    end_date=end_date.strftime('%Y-%m-%d')
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
from generate_price_chart import generate_price_chart_page
try:
    generate_price_chart_page()
except Exception as e:
    print(f"Error generating price chart: {e}")

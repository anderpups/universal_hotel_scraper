import requests
import json
import pandas
import pprint
import time
import random
from datetime import datetime, date, timedelta
from bs4 import BeautifulSoup

today = datetime.now()
tomorrow = today + timedelta(days=1)
date_range = pandas.date_range(start=tomorrow, periods=2)
hotel_info = []

def get_data_for_date(date):
  params = {
    'hgID': 641,
    'langID': 1,
    'checkin': date,
    'nights': 1,
    'adults': 2,
    'children': 0,
    'promo': 'aph',
    'iata': '',
    'group': '',
    'hotels': '',
    'ada': ''
  }
  html = requests.get('https://reservations.universalorlando.com/ibe/default.aspx', params=params)
  soup = BeautifulSoup(html.text, 'html.parser')
  hotels_html = soup.find('section', id='cnWsResultHotels')
  hotels = hotels_html.find_all('div', class_='ws-property-item')
  global date_info
  date_info = {"date": date}
  date_info["hotels"] = []
  for hotel in hotels:
    hotel_name = hotel.find('div', class_='ws-property-title').h1.a.text
    hotel_price = hotel.find('div', class_='ws-property-price').span.text
    date_info['hotels'].append({"name": hotel_name, "price": hotel_price})


for date in date_range:
  print('Grabbing hotel price data for ' + str(date.strftime('%m/%d/%Y')))
  get_data_for_date(date.strftime('%m/%d/%Y'))
  hotel_info.append(date_info)
  random_ms = random.randint(1000,60000)
  random_second = random_ms / 1000
  random_minute = random_second /60
  print('Sleeping for ' + str(round(random_minute, 2)) + ' minutes')
  time.sleep(random_second)

print(hotel_info)

with open("hotel_info.json", "wt") as file:
  pprint.pprint(json.dumps(hotel_info), stream=file)

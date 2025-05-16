import requests
import json
import pandas
import time
import random
from datetime import datetime, timedelta
from bs4 import BeautifulSoup

today = datetime.now()
tomorrow = today + timedelta(days=1)

## Generate a list of 365 random dates starting from tomorrow
date_range = list(pandas.date_range(start=tomorrow, periods=365, freq='D'))
random.shuffle(date_range)

hotel_info = []

## Words we want to remove from the Hotel names
words_to_remove = ["Loews", "Hotel", "Universal", "Inn and Suites", "Resort", ", a", "Endless Summer - ", "Beach", "Grand"]

## Function to remove a list of words from a string using replace()
def remove_words_loop(text, words_to_remove):
  """Removes a list of words from a string using a loop and replace()."""
  new_text = text
  for word in words_to_remove:
    new_text = new_text.replace(word, '')
    new_text = new_text.replace("  "," ")
    new_text = new_text.strip()
  return new_text

## Function to fetch hotel data for a specific date
## and return a list of dictionaries with hotel name, price, and date
## The function takes a date string in the format MM/DD/YYYY
def get_hotel_data_for_date(date):
  """
  Fetch hotel data for a specific date string (MM/DD/YYYY).
  Returns a list of dictionaries with hotel name price and date.
  """
  ## Set the query parameters for the web request
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
  dt = datetime.strptime(date, '%m/%d/%Y')
  try:
    ## Make the web request to the Universal Orlando website
    response = requests.get('https://reservations.universalorlando.com/ibe/default.aspx', params=params, timeout=15)
    ## Check if the response is successful
    response.raise_for_status()
    ## Parse the response content using BeautifulSoup
    ## and extract the hotel price info
    soup = BeautifulSoup(response.text, 'html.parser')
    hotels_html = soup.find('section', id='cnWsResultHotels')
    if not hotels_html:
      return []
    hotels = hotels_html.find_all('div', class_='ws-property-item')
    hotels_list = []
    for hotel in hotels:
      try:
        hotel_name = remove_words_loop((hotel.find('div', class_='ws-property-title').h1.a.text), words_to_remove)
        hotel_price = int((hotel.find('div', class_='ws-property-price').span.text).replace("$",""))
        hotels_list.append({"name": hotel_name, "price": hotel_price,"date": date})
      except Exception as e:
        print(f"Error parsing hotel info: {e}")
    return hotels_list
  except Exception as e:
    print(f"Error fetching data for {date}: {e}")
    return []


## !!! Should only grab the years once, then parse the html multiple times ##
# def get_crowd_info_for_date(date):
#   try:
#     year = date.strftime('%Y')
#     response = requests.get(f'https://www.thrill-data.com/trip-planning/crowd-calendar/resort/uor/{year}', timeout=15)
#     print(response)
#   except Exception as e:
#     print(f"Error fetching data for {date}: {e}")
#     return 'N/A'

## Loop through the date range and fetch hotel data
for date in date_range:
  date_str = date.strftime('%m/%d/%Y')
  date_info = get_hotel_data_for_date(date_str)
  # crowd_info = get_crowd_info_for_date(date)
  hotel_info.extend(date_info)
  print(f"Found {len(date_info)} hotels available for {date_str}")
  sleep_seconds = random.uniform(1, 6)
  time.sleep(sleep_seconds)

## create filename with today's date
filename = f"data/hotel_info-{today.strftime('%Y%m%d')}.json"

## Write the data to a JSON file
with open(filename, "w") as file:
  json.dump(hotel_info, file, indent=2)

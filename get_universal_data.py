import requests
import json
import pandas
import time
import random
import re
from datetime import datetime, timedelta
from bs4 import BeautifulSoup
import sys
from zoneinfo import ZoneInfo

lookahead_period = 365

## Get todday
today = datetime.now(ZoneInfo("America/New_York"))

## Get tomorrow
tomorrow = today + timedelta(days=1)

## Get the end date
end_date = today + timedelta(days=lookahead_period)

## Get the year for today and the end date
years = [(tomorrow.strftime('%Y')), (end_date.strftime('%Y'))]

## Get unique years
years = set(years)

## Generate a list of daterenders starting from tomorrow
date_range = list(pandas.date_range(start=tomorrow, periods=lookahead_period, freq='D'))

## Shuffle the date range
random.shuffle(date_range)

hotel_info = []

data_folder = 'html/data'

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
  try:
    ## Make the web request to the Universal Orlando website
    response = requests.get('https://reservations.universalorlando.com/ibe/default.aspx', params=params, timeout=15)
    ## Check if the response is successful
    response.raise_for_status()
    ## Parse the response content using BeautifulSoup
    ## and extract the hotel price info
    soup = BeautifulSoup(response.text, 'html.parser')
    hotels_html = soup.find('section', id='cnWsResultHotels')
    ## If hotels_html is None, return an empty list
    if not hotels_html:
      return []
    ## Find the html division containing the hotel items
    hotels = hotels_html.find_all('div', class_='ws-property-item')
    ## Initialize an empty list to store the hotel data
    hotels_list = []
    ## Loop through the hotel items and extract the name and price
    for hotel in hotels:
      try:
        ## Get the hotel name and use the funcition remove_words_loop to remove the unwanted words
        hotel_name = remove_words_loop((hotel.find('div', class_='ws-property-title').h1.a.text), words_to_remove)
        ## Get the hotel price and convert it to an integer
        hotel_price = int((hotel.find('div', class_='ws-property-price').span.text).replace("$",""))
        ## Append the hotel data to the list
        hotels_list.append({"name": hotel_name, "price": hotel_price,"date": datetime.strptime(date, "%m/%d/%Y").strftime("%m/%d/%y")})
      except Exception as e:
        print(f"Error parsing hotel info: {e}")
    return hotels_list
  except Exception as e:
    print(f"Error fetching data for {date}: {e}")
    return []

## Function to get the crowd info for a year
def crowd_info():
  try:
    ## Make the web request to thrill-data website
    response = requests.get(f'https://oi-nest-prod-ff3c6f88c478.herokuapp.com/crowd/levels', timeout=15)
    response.raise_for_status()
    response_json = response.json()
    # Parse the input string into a datetime object

# Format the datetime object into the desired output string
    crowd_info = [{"date": datetime.strptime(item["date"], "%Y-%m-%d").strftime("%m/%d/%y"), "crowd_info": int(item["crowd"]["crowdScore"] * 100)} for item in response_json["responseObject"]]
    return(crowd_info)
  except Exception as e:
    print(f"Error fetching crowd info: {e}")
    sys.exit(1)

crowd_info = crowd_info()

## Loop through the date range and fetch hotel data
for date in date_range:
  date_str = date.strftime('%m/%d/%Y')
  ## get the hotel data for the date
  date_info = get_hotel_data_for_date(date_str)
  hotel_info.extend(date_info)
  print(f"Found {len(date_info)} hotels available for {date_str}")
  print(f'Dates left to process: {len(date_range) - date_range.index(date) - 1}')
  sleep_seconds = random.uniform(1, 2)
  time.sleep(sleep_seconds)

# create filename with today's date
filename = f"{today.strftime('%Y%m%d')}.json"

## Write the data to a JSON file
with open(f"{data_folder}/hotel_info-{filename}", "w") as file:
  json.dump(hotel_info, file, indent=2)

with open(f"{data_folder}/crowd_info-{filename}", "w") as file:
  json.dump(crowd_info, file, indent=2)

import requests
import json
import yaml
import os
import pandas
import time
import random
import re
from datetime import datetime, timedelta
from bs4 import BeautifulSoup
import smtplib
from jinja2 import Environment, FileSystemLoader
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

lookahead_period = 365

## Get todday
today = datetime.now()

## Get tomorrow
tomorrow = today + timedelta(days=1)

## Get the end date
end_date = today + timedelta(days=lookahead_period)

## Get the year for today and the end date
years = [(tomorrow.strftime('%Y')), (end_date.strftime('%Y'))]

## Get unique years
years = set(years)

## Generate a list of dates starting from tomorrow
date_range = list(pandas.date_range(start=tomorrow, periods=lookahead_period, freq='D'))

## Shuffle the date range
random.shuffle(date_range)

hotel_info = []

data_folder = 'html/data'

environment = Environment(loader=FileSystemLoader("templates/"))
price_alert_email_template = environment.get_template("price-alert-email.html.j2")

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
def get_crowd_info(year):
  try:
    ## Make the web request to thrill-data website
    response = requests.get(f'https://www.thrill-data.com/trip-planning/crowd-calendar/islands-of-adventure/calendar/{year}', timeout=15)
    response.raise_for_status()
    ## Parse the response content using BeautifulSoup
    soup = BeautifulSoup(response.text, 'html.parser')
    ## Find the html division containing the calendar table
    calendar_table = soup.find('table', class_='calendar-table')
    ## Initialize an empty list to store the crowd data
    data = []
    ## Get the table rows
    rows = calendar_table.find_all('td')  # Get all the data cells
    ## Loop through the table rows and extract the date and wait time
    for row in rows:
        ## Get the link inside the row
        link = row.find('a')
        ## If the link is not None, extract the date and wait time
        if link:
            date_div = link.find('div', class_='button-set-label')
            crowd_info_div = link.find('div', class_='calendar-box')
            if date_div and crowd_info_div:
                date = date_div.text.strip()
                ## Add the year to the date
                date = (f'{date} {year}')
                ## Convert the date to a datetime object
                date = datetime.strptime(date, "%b %d %Y")
                crowd_info = crowd_info_div.text.strip()
                ## Append the date and wait time to the data list
                data.append({'date': date.strftime("%m/%d/%y"), 'crowd_info': int(crowd_info)})
    return(data)
  except Exception as e:
    return []

## Function to get the crowd info for the date range
def get_crowd_info_dates(crowd_info, date_range):
  matching_crowd_info = []
  ## Loop through the crowd info
  for crowd_item in crowd_info:
    ## Loop through the date range
    for date in date_range:
      ## Check if the date in the crowd info is in the date range
      if crowd_item['date'] == date.strftime('%m/%d/%y'):
        ## If it is, append the crowd info to the matching_crowd_info list
        matching_crowd_info.append(crowd_item)
  return matching_crowd_info

def send_html_email(filtered_hotel_info, price_alert):
    ## Define vars
    if 'emails' in price_alert:
      recipients_email = ", ".join(price_alert['emails'])
    else:
       recipients_email = 'anderpups@gmail.com'
    sender_email = "universal.hotel.price.alert@gmail.com"  # Your Gmail address
    app_password = (os.environ['GMAIL_APP_PASSWORD'])
    ## This is dumb, should make better
    if 'hotel' in price_alert:
      subject = f'Universal Hotel Price Alert for {price_alert["hotel"]}'
    elif 'date' in price_alert:
      subject = f'Universal Hotel Price Alert for {price_alert["date"]}'
    elif 'price' in price_alert:
      subject = f'Universal Hotel Price Alert for {price_alert["price"]}'
    else:
      subject = f'Universal Hotel Price Alert for lowest price'   
    # Create the root message and set the headers
    # Using 'alternative' is important for HTML emails
    msg = MIMEMultipart('alternative')
    msg['From'] = sender_email
    msg['To'] = sender_email
    msg['Bcc'] = recipients_email 
    msg['Subject'] = subject

    html_content = price_alert_email_template.render(
    filtered_hotel_info=filtered_hotel_info,
    price_alert=price_alert)

    # According to RFC 2046, the last part of a multipart message, in this case
    # the HTML message, is best and preferred.
    msg.attach(MIMEText(html_content, 'html'))
    try:
        server = smtplib.SMTP_SSL('smtp.gmail.com', 465)
        server.login(sender_email, app_password)
        server.sendmail(sender_email, recipients_email, msg.as_string())
        
    except smtplib.SMTPAuthenticationError:
        print("Authentication failed. Please check your email and app password.")
    except Exception as e:
        print(f"An error occurred: {e}")
    finally:
        if 'server' in locals() and server:
            server.quit()

crowd_info = []

## Loop through the years and fetch crowd data
for year in years:
  print(f"Fetching crowd data for {year}")
  crowd_info = (crowd_info + get_crowd_info(year))

## Loop through the date range and fetch hotel data
for date in date_range:
  date_str = date.strftime('%m/%d/%Y')
  ## get the hotel data for the date
  date_info = get_hotel_data_for_date(date_str)
  hotel_info.extend(date_info)
  print(f"Found {len(date_info)} hotels available for {date_str}")
  sleep_seconds = random.uniform(1, 2)
  time.sleep(sleep_seconds)

crowd_info = get_crowd_info_dates(crowd_info, date_range)

# create filename with today's date
filename = f"{today.strftime('%Y%m%d')}.json"

## Write the data to a JSON file
with open(f"{data_folder}/hotel_info-{filename}", "w") as file:
  json.dump(hotel_info, file, indent=2)

with open(f"{data_folder}/crowd_info-{filename}", "w") as file:
  json.dump(crowd_info, file, indent=2)

## Get price alerts
with open('price_alerts.yaml', 'r') as file:
  price_alerts = yaml.safe_load(file)

for price_alert in price_alerts:  
  filtered_hotel_info = hotel_info
  if 'hotel' in price_alert:
    filtered_hotel_info = [hotel for hotel in filtered_hotel_info if hotel['name'] == price_alert['hotel']]
  if 'dates' in price_alert:
    filtered_hotel_info = [hotel for hotel in filtered_hotel_info if hotel['date'] in price_alert['dates']]
  if 'price' in price_alert:
    filtered_hotel_info = [hotel for hotel in filtered_hotel_info if int(hotel['price']) <= int(price_alert['price'])]
  else:
    lowest_price = min(int(hotel['price']) for hotel in filtered_hotel_info)
    filtered_hotel_info = [hotel for hotel in filtered_hotel_info if int(hotel['price']) == int(lowest_price)]
  if filtered_hotel_info:
    send_html_email(filtered_hotel_info, price_alert)

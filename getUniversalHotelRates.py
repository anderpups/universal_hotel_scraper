import requests
from bs4 import BeautifulSoup

def hotel_data(date):
  html = requests.get('https://reservations.universalorlando.com/ibe/default.aspx?hgID=641&langID=1&checkin='+ date +'&nights=1&rooms=1&adults=2&children=0&promo=aph&iata=&group=&hotels=&ada=')
  print(html)
  # soup = BeautifulSoup(html, 'html.parser')
  # hotels_html = soup.find('section', id='cnWsResultHotels')
  # hotels = hotels_html.find_all('div', class_='ws-property-item')
  # global date_info
  # date_info = {'date': date, hotels:[]}
  # for hotel in hotels:
  #   hotel_name = hotel.find('div', class_='ws-property-title').h1.a.text
  #   hotel_price = hotel.find('div', class_='ws-property-price').span.text
  #   date_info.hotels.append[{"name": hotel_name, "price": hotel_price}]

hotel_data('9/25/2025')

# print(date_info)
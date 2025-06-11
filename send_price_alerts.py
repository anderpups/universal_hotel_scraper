import glob
import json
import yaml
import os
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import smtplib
from jinja2 import Environment, FileSystemLoader
import time

data_folder = 'html/data'

environment = Environment(loader=FileSystemLoader("templates/"))
price_alert_email_template = environment.get_template("price-alert-email.html.j2")

def send_html_email(filtered_hotel_info, price_alert):
    ## Define vars
    if 'emails' in price_alert:
      recipients_email = ", ".join(price_alert['emails'])
    else:
       recipients_email = 'anderpups@gmail.com, heatherschorah@yahoo.com'
    sender_email = "universal.hotel.price.alert@gmail.com"  # Your Gmail address
    app_password = (os.environ['GMAIL_APP_PASSWORD'])
    ## This is dumb, should make better
    if 'hotel' in price_alert:
      subject = f'Universal Hotel Price Alert for {price_alert["hotel"]}'
    if 'hotels' in price_alert:
       subject = f'Universal Hotel Price Alert for {", ".join(price_alert["hotels"])}'
    elif 'dates' in price_alert:
      subject = f'Universal Hotel Price Alert for {" ".join(price_alert["dates"])}'
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

## Find all hotel_info JSON files in the data folder
hotel_info_json_files = glob.glob(os.path.join(data_folder, "hotel_info*.json"))
hotel_info_json_files.sort(reverse=True)

with open(hotel_info_json_files[0], 'r') as f:
    hotel_info = json.load(f)

## Get price alerts
with open('price_alerts.yaml', 'r') as file:
  price_alerts = yaml.safe_load(file)

for price_alert in price_alerts:  
  filtered_hotel_info = hotel_info
  if 'hotels' in price_alert:
    filtered_hotel_info = [hotel for hotel in filtered_hotel_info if hotel['name'] in price_alert['hotels']]
  if 'hotel' in price_alert:
    filtered_hotel_info = [hotel for hotel in filtered_hotel_info if hotel['name'] == price_alert['hotel']]
  if 'dates' in price_alert:
    filtered_hotel_info = [hotel for hotel in filtered_hotel_info if hotel['date'] in price_alert['dates']]
  if 'price' in price_alert and type(price_alert['price']) == int:
    filtered_hotel_info = [hotel for hotel in filtered_hotel_info if int(hotel['price']) <= int(price_alert['price'])]
  elif 'price' not in price_alert:
    lowest_price = min(int(hotel['price']) for hotel in filtered_hotel_info)
    filtered_hotel_info = [hotel for hotel in filtered_hotel_info if int(hotel['price']) == int(lowest_price)]
  if filtered_hotel_info:
    send_html_email(filtered_hotel_info, price_alert)

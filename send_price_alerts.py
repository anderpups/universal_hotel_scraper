import glob
import json
import yaml
import os
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import smtplib
from jinja2 import Environment, FileSystemLoader

data_folder = 'html/data'

environment = Environment(loader=FileSystemLoader("templates/"))
price_alert_email_template = environment.get_template("price-alert-email.html.j2")

def send_html_email(recipient_email, triggered_alerts):
    sender_email = "universal.hotel.price.alert@gmail.com"  # Your Gmail address
    app_password = (os.environ['GMAIL_APP_PASSWORD'])
    
    # Generic subject for grouped alerts
    subject = f'Universal Hotel Price Alerts: {len(triggered_alerts)} Alerts Triggered'
    
    # Create the root message and set the headers
    msg = MIMEMultipart('alternative')
    msg['From'] = sender_email
    msg['To'] = recipient_email
    msg['Subject'] = subject

    html_content = price_alert_email_template.render(
        triggered_alerts=triggered_alerts
    )

    # According to RFC 2046, the last part of a multipart message, in this case
    # the HTML message, is best and preferred.
    msg.attach(MIMEText(html_content, 'html'))
    try:
        server = smtplib.SMTP_SSL('smtp.gmail.com', 465)
        server.login(sender_email, app_password)
        server.sendmail(sender_email, recipient_email, msg.as_string())
        print(f"Sent email to {recipient_email} with {len(triggered_alerts)} alerts.")
        
    except smtplib.SMTPAuthenticationError:
        print("Authentication failed. Please check your email and app password.")
    except Exception as e:
        print(f"An error occurred: {e}")
    finally:
        if 'server' in locals() and server:
            server.quit()

## Find all hotel-prices JSON files in the data folder
# Updated glob pattern to match the new file naming convention
hotel_info_json_files = glob.glob(os.path.join(data_folder, "hotel-prices-*.json"))
hotel_info_json_files.sort(reverse=True)

if not hotel_info_json_files:
    print(f"No hotel price files found in {data_folder}")
    exit()

with open(hotel_info_json_files[0], 'r') as f:
    raw_data = json.load(f)

# Transform the new nested JSON structure into the flat list structure the script expects
hotel_info = []
for entry in raw_data:
    current_date = entry.get('date')
    # The new JSON has a 'prices' list inside each date entry
    for price_entry in entry.get('prices', []):
        hotel_info.append({
            'name': price_entry.get('hotel'),
            'date': current_date,
            'price': price_entry.get('aph_price')
        })

## Get price alerts
with open('price_alerts.yaml', 'r') as file:
  price_alerts = yaml.safe_load(file)

# Dictionary to hold alerts grouped by recipient email
# Structure: { 'email@example.com': [ { 'criteria': alert_dict, 'matches': list_of_hotels }, ... ] }
alerts_by_recipient = {}
default_recipients = ["anderpups@gmail.com"]

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
    if filtered_hotel_info: # Check to ensure list is not empty before min()
        lowest_price = min(int(hotel['price']) for hotel in filtered_hotel_info)
        filtered_hotel_info = [hotel for hotel in filtered_hotel_info if int(hotel['price']) == int(lowest_price)]
  
  # If triggers found, assign to recipients
  if filtered_hotel_info:
    recipients = price_alert.get('emails', default_recipients)
    # Ensure recipients is a list (handle single string case)
    if isinstance(recipients, str):
        recipients = [recipients]
    
    for email in recipients:
        if email not in alerts_by_recipient:
            alerts_by_recipient[email] = []
        
        alerts_by_recipient[email].append({
            'criteria': price_alert,
            'matches': filtered_hotel_info
        })

# Send one email per recipient containing all their alerts
for recipient, alerts_list in alerts_by_recipient.items():
    send_html_email(recipient, alerts_list)
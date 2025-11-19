import glob
import json
import os
from datetime import datetime, timedelta
from jinja2 import Environment, FileSystemLoader

def generate_price_chart_page():
    """Generate an interactive line chart page for hotel prices over time."""
    
    try:
        html_folder = 'html'
        data_folder = f'{html_folder}/data'
        chart_html_file = os.path.join(html_folder, "price_chart.html")
        
        print(f"Looking for data in: {data_folder}")
        
        # Set up Jinja environment
        environment = Environment(loader=FileSystemLoader("templates/"))
        chart_template = environment.get_template("price-chart.html.j2")
        
        # Find all JSON files in the data folder and sort them
        hotel_info_json_files = glob.glob(os.path.join(data_folder, "hotel_info*.json"))
        hotel_info_json_files.sort()
        
        print(f"Found {len(hotel_info_json_files)} hotel info files")
        
        # Get today's date for filtering
        today = datetime.now()
        
        # Dictionary to store data by hotel and gather date
        all_hotel_data = {}
        
        print("Processing hotel data files...")
        
        # Process each JSON file
        for file_path in hotel_info_json_files:
            filename = os.path.basename(file_path)
            gather_date_str = filename.split("-")[1].split(".")[0]
            
            # Parse gather date
            try:
                gather_date = datetime.strptime(gather_date_str, "%Y%m%d")
            except ValueError:
                print(f"Skipping file with invalid date format: {filename}")
                continue
                
            # Skip if gather date is more than 365 days ago (process up to 1 year of data)
            if (today - gather_date).days > 365:
                continue
                
            # Load the data
            try:
                with open(file_path, "r") as f:
                    data = json.load(f)
            except Exception as e:
                print(f"Error reading {file_path}: {e}")
                continue
            
            # Process each hotel entry
            for entry in data:
                hotel_name = entry['name']
                price = entry['price']
                stay_date = entry['date']
                
                # Initialize hotel data structure if needed
                if hotel_name not in all_hotel_data:
                    all_hotel_data[hotel_name] = {}
                
                if gather_date_str not in all_hotel_data[hotel_name]:
                    all_hotel_data[hotel_name][gather_date_str] = {}
                
                # Store the price for this stay date
                all_hotel_data[hotel_name][gather_date_str][stay_date] = price
        
        print(f"Processed data for {len(all_hotel_data)} hotels")
        
        # Convert data to a format suitable for Chart.js
        chart_data = []
        hotel_colors = [
            '#FF6B6B', '#4ECDC4', '#45B7D1', '#FFA07A', '#98D8C8', 
            '#F7DC6F', '#BB8FCE', '#85C1E9', '#F8C471', '#82E0AA',
            '#F1948A', '#85C1E9', '#D7BDE2', '#A9DFBF', '#FAD7A0'
        ]
        
        for idx, (hotel_name, gather_dates) in enumerate(all_hotel_data.items()):
            color = hotel_colors[idx % len(hotel_colors)]
            
            # For each stay date, find the most recent price data
            stay_date_prices = {}
            
            # Get all unique stay dates across all gather dates
            all_stay_dates = set()
            for dates_data in gather_dates.values():
                all_stay_dates.update(dates_data.keys())
            
            # For each stay date, collect prices from different gather dates
            for stay_date in all_stay_dates:
                price_history = []
                
                for gather_date_str in sorted(gather_dates.keys()):
                    if stay_date in gather_dates[gather_date_str]:
                        price = gather_dates[gather_date_str][stay_date]
                        gather_date = datetime.strptime(gather_date_str, "%Y%m%d")
                        price_history.append({
                            'gather_date': gather_date.strftime('%Y-%m-%d'),
                            'price': price
                        })
                
                if price_history:
                    stay_date_prices[stay_date] = price_history
            
            chart_data.append({
                'hotel_name': hotel_name,
                'color': color,
                'stay_dates': stay_date_prices
            })
        
        # Get list of all gather dates for the time period selector
        all_gather_dates = set()
        for file_path in hotel_info_json_files:
            filename = os.path.basename(file_path)
            gather_date_str = filename.split("-")[1].split(".")[0]
            try:
                gather_date = datetime.strptime(gather_date_str, "%Y%m%d")
                if (today - gather_date).days <= 365:
                    all_gather_dates.add(gather_date_str)
            except ValueError:
                continue
        
        all_gather_dates = sorted(list(all_gather_dates))
        
        # Render the template
        html_content = chart_template.render(
            chart_data_json=json.dumps(chart_data),
            all_gather_dates=all_gather_dates,
            today=today.strftime('%Y-%m-%d')
        )
        
        # Write the HTML file
        with open(chart_html_file, "w") as f:
            f.write(html_content)
        
        print(f"Generated price chart page: {chart_html_file}")
        print(f"Found {len(chart_data)} hotels with price data")
        
    except Exception as e:
        print(f"Error in generate_price_chart_page: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    generate_price_chart_page()
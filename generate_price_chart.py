import glob
import os
from datetime import datetime
from jinja2 import Environment, FileSystemLoader

def generate_price_chart_page():
    """
    Generate the price chart HTML page. 
    Instead of processing data here, this script scans for available data files
    and passes the file list to the template so the browser can fetch them.
    """
    
    try:
        html_folder = 'html'
        data_folder = f'{html_folder}/data'
        chart_html_file = os.path.join(html_folder, "price_chart.html")
        
        print(f"Scanning for data files in: {data_folder}")
        
        # Set up Jinja environment
        environment = Environment(loader=FileSystemLoader("templates/"))
        chart_template = environment.get_template("price-chart.html.j2")
        
        # Find all JSON files
        # Updated to match hotel-prices-YYYYMMDD.json
        hotel_prices_json_files = glob.glob(os.path.join(data_folder, "hotel-prices-*.json"))
        hotel_prices_json_files.sort()
        
        today = datetime.now()
        
        # Build a list of available data files to pass to JavaScript
        data_files = []
        
        for file_path in hotel_prices_json_files:
            filename = os.path.basename(file_path)
            # Filename format expected: hotel-prices-20250514.json
            try:
                # Split 'hotel-prices-20250514.json' by '-' -> ['hotel', 'prices', '20250514.json']
                date_part = filename.split("-")[2].split(".")[0]
                gather_date = datetime.strptime(date_part, "%Y%m%d")
                
                # Filter out files older than 365 days to keep the fetch list reasonable
                if (today - gather_date).days > 365:
                    continue
                
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
        
        print(f"Generated price chart page: {chart_html_file}")
        
    except Exception as e:
        print(f"Error in generate_price_chart_page: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    generate_price_chart_page()
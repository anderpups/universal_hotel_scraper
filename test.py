import glob
import os
import json

def optimize_hotel_data():
    """
    Scans for hotel-data-*.json files, aggregates data by check-in date,
    and saves optimized, minified JSON files with the prefix hotel-prices-*.
    """
    html_folder = 'html'
    data_folder = f'{html_folder}/data'
    
    # Find all source JSON files
    hotel_info_files = glob.glob(os.path.join(data_folder, "hotel-data-*.json"))
    
    print(f"Found {len(hotel_info_files)} files to process.")
    
    for file_path in hotel_info_files:
        try:
            # Extract the gather date from the filename (e.g., 20250514)
            filename = os.path.basename(file_path)
            # Expected format: hotel-data-YYYYMMDD.json
            date_part = filename.replace("hotel-data-", "").replace(".json", "")
            
            # Read the original inefficient data
            with open(file_path, 'r') as f:
                original_data = json.load(f)
            
            # Group data by check-in date
            # Structure: { "MM/DD/YY": { "date": "...", "crowd_level": ..., "prices": [] } }
            grouped_data = {}
            
            for entry in original_data:
                check_in_date = entry.get('date')
                
                # If this date hasn't been processed yet, initialize the structure
                if check_in_date not in grouped_data:
                    grouped_data[check_in_date] = {
                        "date": check_in_date,
                        "crowd_level": entry.get('crowd_level'),
                        "prices": []
                    }
                
                # Create the simplified hotel price object
                hotel_price = {
                    "hotel": entry.get('name'),
                    "aph_price": entry.get('price')
                }
                
                grouped_data[check_in_date]["prices"].append(hotel_price)
            
            # Convert the grouping dictionary values to a list
            optimized_data_list = list(grouped_data.values())
            
            # Define new filename
            new_filename = f"hotel-prices-{date_part}.json"
            new_file_path = os.path.join(data_folder, new_filename)
            
            # Write the minified JSON
            with open(new_file_path, 'w') as f:
                # separators=(',', ':') removes whitespace
                json.dump(optimized_data_list, f, separators=(',', ':'))
                
            print(f"Processed {filename} -> {new_filename}")

        except Exception as e:
            print(f"Error processing {file_path}: {e}")

if __name__ == "__main__":
    optimize_hotel_data()
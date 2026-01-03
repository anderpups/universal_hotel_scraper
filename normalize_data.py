import json
import os

def normalize_files(dates, base_dir='html/data'):
    """
    Reads separate crowd_info and hotel_info files for the given dates
    and creates a unified hotel-prices file for each.
    """
    for date_suffix in dates:
        crowd_file = os.path.join(base_dir, f'crowd_info-{date_suffix}.json')
        hotel_file = os.path.join(base_dir, f'hotel_info-{date_suffix}.json')
        output_file = os.path.join(base_dir, f'hotel-prices-{date_suffix}.json')

        if not os.path.exists(crowd_file) or not os.path.exists(hotel_file):
            print(f"Skipping {date_suffix}: Source files not found.")
            continue

        print(f"Processing {date_suffix}...")

        # Load raw data
        with open(crowd_file, 'r') as f:
            crowd_data = json.load(f)
        
        with open(hotel_file, 'r') as f:
            hotel_data = json.load(f)

        # Dictionary to merge data by date key (e.g., "09/15/26")
        merged_data = {}

        # 1. Process Crowd Info
        # Source format: [{"date": "01/01/26", "crowd_info": 100}, ...]
        for entry in crowd_data:
            date_key = entry.get('date')
            if date_key:
                if date_key not in merged_data:
                    merged_data[date_key] = {
                        "date": date_key,
                        "crowd_level": 0, # Default
                        "prices": []
                    }
                # Map 'crowd_info' to 'crowd_level'
                merged_data[date_key]["crowd_level"] = entry.get('crowd_info', 0)

        # 2. Process Hotel Info
        # Source format: [{"name": "Terra Luna", "price": 235, "date": "09/15/26"}, ...]
        for entry in hotel_data:
            date_key = entry.get('date')
            if date_key:
                if date_key not in merged_data:
                    # Initialize if we have price data but no crowd data yet
                    merged_data[date_key] = {
                        "date": date_key,
                        "crowd_level": 0,
                        "prices": []
                    }
                
                # Map fields to target format
                price_entry = {
                    "hotel": entry.get('name'),      # 'name' -> 'hotel'
                    "aph_price": entry.get('price')  # 'price' -> 'aph_price'
                }
                merged_data[date_key]["prices"].append(price_entry)

        # Convert merged dictionary back to a list
        final_output = list(merged_data.values())

        # Write to the new file
        with open(output_file, 'w') as f:
            json.dump(final_output, f, separators=(',', ':')) # Minified format like source
        
        print(f"Created {output_file}")

if __name__ == "__main__":
    # The dates where files are split
    target_dates = ['20260101', '20260102', '20260103']
    
    # Run normalization
    # Assumes script is running from the root of the repo; adjust path if needed
    normalize_files(target_dates, base_dir='html/data')
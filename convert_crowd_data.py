import json
import glob
import os

def combine_hotel_and_crowd_data():
    """
    Combines crowd data gathered on each day with the hotel data gathered on that day.
    
    1. Scans 'html/data' for 'hotel_info-*.json' files.
    2. Finds the corresponding 'crowd_info-*.json' file for the same date.
    3. Merges the 'crowd_info' value into the hotel data as 'crowd_level'.
    4. Saves the result to a new file with the prefix 'hotel-data'.
    """
    
    # Define the directory containing the data files
    # Assuming this script is run from the project root
    data_folder = os.path.join('html', 'data')
    
    # Find all hotel_info files
    hotel_files = glob.glob(os.path.join(data_folder, "hotel_info-*.json"))
    hotel_files.sort()
    
    print(f"Found {len(hotel_files)} hotel info files to process in {data_folder}...")
    
    for hotel_file_path in hotel_files:
        try:
            # Extract the date part from the filename
            # Expected format: hotel_info-20250514.json -> 20250514
            filename = os.path.basename(hotel_file_path)
            date_part = filename.split("-")[1].split(".")[0]
            
            # Construct the path for the corresponding crowd info file
            crowd_file_path = os.path.join(data_folder, f"crowd_info-{date_part}.json")
            
            # Load the hotel data
            with open(hotel_file_path, 'r') as f:
                hotel_data = json.load(f)
            
            # Load the crowd data if it exists and create a lookup dictionary
            crowd_lookup = {}
            if os.path.exists(crowd_file_path):
                with open(crowd_file_path, 'r') as f:
                    crowd_source_data = json.load(f)
                    
                # Create a dictionary mapping date -> crowd_info for faster lookup
                # Source format: [{"date": "MM/DD/YY", "crowd_info": 36}, ...]
                for item in crowd_source_data:
                    if "date" in item and "crowd_info" in item:
                        crowd_lookup[item["date"]] = item["crowd_info"]
            else:
                print(f"  Notice: No crowd info file found for {date_part}. 'crowd_level' will be 'none'.")

            # Process each hotel entry to add the crowd_level
            combined_data = []
            for entry in hotel_data:
                # entry format: {"name": "...", "price": ..., "date": "MM/DD/YY"}
                check_in_date = entry.get("date")
                
                # Retrieve crowd level from lookup, default to "none" if missing
                crowd_val = crowd_lookup.get(check_in_date)
                
                # If crowd_val is None (key missing) it defaults to "none" string
                entry["crowd_level"] = crowd_val if crowd_val is not None else "none"
                
                combined_data.append(entry)
            
            # Construct the new filename
            new_filename = f"hotel-data-{date_part}.json"
            new_file_path = os.path.join(data_folder, new_filename)
            
            # Write the combined data to the new file
            with open(new_file_path, 'w') as f:
                json.dump(combined_data, f, indent=4)
                
            print(f"  Generated: {new_filename}")

        except Exception as e:
            print(f"Error processing {hotel_file_path}: {e}")

if __name__ == "__main__":
    combine_hotel_and_crowd_data()
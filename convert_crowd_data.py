import json
import os
import glob
from datetime import datetime

# ---------------------------------------------------------
# 1. RAW WAIT TIME DATA (From Thrill-Data, Year 2025)
# ---------------------------------------------------------
raw_wait_data = """
Jan 01
35
Jan 02
55
Jan 03
44
Jan 04
42
Jan 05
39
Jan 06
30
Jan 07
33
Jan 08
30
Jan 09
29
Jan 10
27
Jan 11
32
Jan 12
25
Jan 13
25
Jan 14
26
Jan 15
23
Jan 16
30
Jan 17
30
Jan 18
44
Jan 19
38
Jan 20
41
Jan 21
16
Jan 22
22
Jan 23
25
Jan 24
30
Jan 25
48
Jan 26
30
Jan 27
29
Jan 28
28
Jan 29
29
Jan 30
27
Jan 31
24
Feb 01
34
Feb 02
26
Feb 03
24
Feb 04
25
Feb 05
24
Feb 06
29
Feb 07
27
Feb 08
37
Feb 09
33
Feb 10
30
Feb 11
24
Feb 12
19
Feb 13
25
Feb 14
38
Feb 15
45
Feb 16
43
Feb 17
45
Feb 18
50
Feb 19
48
Feb 20
50
Feb 21
44
Feb 22
44
Feb 23
39
Feb 24
16
Feb 25
30
Feb 26
29
Feb 27
26
Feb 28
27
Mar 01
35
Mar 02
29
Mar 03
25
Mar 04
28
Mar 05
19
Mar 06
31
Mar 07
27
Mar 08
33
Mar 09
31
Mar 10
24
Mar 11
44
Mar 12
35
Mar 13
45
Mar 14
50
Mar 15
53
Mar 16
37
Mar 17
44
Mar 18
43
Mar 19
36
Mar 20
38
Mar 21
43
Mar 22
39
Mar 23
32
Mar 24
30
Mar 25
35
Mar 26
33
Mar 27
31
Mar 28
37
Mar 29
36
Mar 30
23
Mar 31
25
Apr 01
27
Apr 02
25
Apr 03
33
Apr 04
41
Apr 05
35
Apr 06
33
Apr 07
25
Apr 08
34
Apr 09
24
Apr 10
28
Apr 11
35
Apr 12
37
Apr 13
37
Apr 14
48
Apr 15
45
Apr 16
44
Apr 17
49
Apr 18
44
Apr 19
47
Apr 20
31
Apr 21
36
Apr 22
31
Apr 23
30
Apr 24
29
Apr 25
28
Apr 26
36
Apr 27
27
Apr 28
22
Apr 29
22
Apr 30
18
May 01
20
May 02
20
May 03
31
May 04
20
May 05
23
May 06
23
May 07
21
May 08
20
May 09
21
May 10
32
May 11
21
May 12
13
May 13
22
May 14
20
May 15
24
May 16
23
May 17
33
May 18
26
May 19
23
May 20
24
May 21
24
May 22
28
May 23
29
May 24
38
May 25
39
May 26
30
May 27
34
May 28
36
May 29
33
May 30
32
May 31
31
Jun 01
30
Jun 02
27
Jun 03
29
Jun 04
24
Jun 05
31
Jun 06
29
Jun 07
31
Jun 08
26
Jun 09
25
Jun 10
25
Jun 11
25
Jun 12
28
Jun 13
25
Jun 14
31
Jun 15
26
Jun 16
27
Jun 17
28
Jun 18
26
Jun 19
29
Jun 20
33
Jun 21
41
Jun 22
31
Jun 23
28
Jun 24
30
Jun 25
27
Jun 26
33
Jun 27
34
Jun 28
36
Jun 29
31
Jun 30
30
Jul 01
28
Jul 02
29
Jul 03
30
Jul 04
28
Jul 05
32
Jul 06
24
Jul 07
27
Jul 08
29
Jul 09
28
Jul 10
30
Jul 11
28
Jul 12
36
Jul 13
27
Jul 14
24
Jul 15
25
Jul 16
31
Jul 17
29
Jul 18
31
Jul 19
34
Jul 20
26
Jul 21
29
Jul 22
31
Jul 23
32
Jul 24
34
Jul 25
35
Jul 26
35
Jul 27
30
Jul 28
31
Jul 29
29
Jul 30
28
Jul 31
26
Aug 01
27
Aug 02
31
Aug 03
31
Aug 04
36
Aug 05
24
Aug 06
34
Aug 07
30
Aug 08
30
Aug 09
35
Aug 10
27
Aug 11
27
Aug 12
27
Aug 13
24
Aug 14
24
Aug 15
25
Aug 16
31
Aug 17
26
Aug 18
26
Aug 19
28
Aug 20
24
Aug 21
23
Aug 22
26
Aug 23
28
Aug 24
21
Aug 25
23
Aug 26
21
Aug 27
20
Aug 28
17
Aug 29
19
Aug 30
32
Aug 31
28
Sep 01
21
Sep 02
24
Sep 03
22
Sep 04
21
Sep 05
20
Sep 06
24
Sep 07
17
Sep 08
19
Sep 09
19
Sep 10
18
Sep 11
19
Sep 12
18
Sep 13
24
Sep 14
19
Sep 15
21
Sep 16
20
Sep 17
19
Sep 18
19
Sep 19
21
Sep 20
22
Sep 21
20
Sep 22
20
Sep 23
22
Sep 24
25
Sep 25
24
Sep 26
20
Sep 27
23
Sep 28
17
Sep 29
18
Sep 30
18
Oct 01
18
Oct 02
18
Oct 03
23
Oct 04
25
Oct 05
24
Oct 06
24
Oct 07
27
Oct 08
28
Oct 09
19
Oct 10
33
Oct 11
34
Oct 12
27
Oct 13
33
Oct 14
32
Oct 15
29
Oct 16
27
Oct 17
29
Oct 18
32
Oct 19
30
Oct 20
27
Oct 21
29
Oct 22
24
Oct 23
23
Oct 24
24
Oct 25
29
Oct 26
23
Oct 27
22
Oct 28
23
Oct 29
23
Oct 30
19
Oct 31
19
Nov 01
24
Nov 02
24
Nov 03
23
Nov 04
30
Nov 05
23
Nov 06
23
Nov 07
27
Nov 08
31
Nov 09
26
Nov 10
23
Nov 11
35
Nov 12
21
Nov 13
23
Nov 14
22
Nov 15
25
Nov 16
18
Nov 17
25
Nov 18
24
Nov 19
24
Nov 20
26
Nov 21
34
Nov 22
39
Nov 23
42
Nov 24
43
Nov 25
44
Nov 26
45
Nov 27
43
Nov 28
41
Nov 29
44
Nov 30
29
Dec 01
25
Dec 02
27
Dec 03
26
Dec 04
30
Dec 05
28
Dec 06
33
Dec 07
31
Dec 08
29
Dec 09
28
Dec 10
30
Dec 11
26
Dec 12
27
Dec 13
29
Dec 14
28
Dec 15
27
Dec 16
24
Dec 17
29
Dec 18
36
Dec 19
39
Dec 20
39
Dec 21
42
Dec 22
42
Dec 23
40
Dec 24
34
Dec 25
37
Dec 26
44
Dec 27
57
Dec 28
52
Dec 29
46
Dec 30
55
Dec 31
41
"""

# ---------------------------------------------------------
# 2. CONFIGURATION
# ---------------------------------------------------------
DATA_DIR = "html/data"
NEW_METRIC_REF_FILE = "crowd_info-20251028.json"
SWITCH_DATE_INT = 20251027  # Files with this date or older will be converted

def parse_wait_times(raw_data):
    """Parses the raw text data into a dict { 'MM/DD/YY': wait_time }"""
    lines = [line.strip() for line in raw_data.strip().split('\n') if line.strip()]
    wait_times = {}
    current_year = 2025 # Assuming the data provided is for the current year in context
    
    for i in range(0, len(lines), 2):
        if i + 1 >= len(lines): break
        date_str = lines[i] # e.g. "Jan 01"
        value = int(lines[i+1])
        
        # Convert "Jan 01" to datetime object to get "MM/DD/YY" format
        dt = datetime.strptime(f"{date_str} {current_year}", "%b %d %Y")
        formatted_date = dt.strftime("%m/%d/%y")
        wait_times[formatted_date] = value
        
    return wait_times

def calculate_correlation(wait_times, percent_full_file_path):
    """Calculates linear regression (slope, intercept) between wait times and percent full."""
    if not os.path.exists(percent_full_file_path):
        print(f"Reference file not found: {percent_full_file_path}")
        return None, None

    with open(percent_full_file_path, 'r') as f:
        new_data = json.load(f)
    
    # Map new data by date
    new_data_map = { entry['date']: entry['crowd_info'] for entry in new_data }
    
    x_vals = [] # Wait Times
    y_vals = [] # Percent Full
    
    common_dates = []
    
    for date, wait in wait_times.items():
        if date in new_data_map:
            full = new_data_map[date]
            # Filter out potentially invalid 0 values if any, though the dataset looks clean
            if full > 0: 
                x_vals.append(wait)
                y_vals.append(full)
                common_dates.append(date)

    if not x_vals:
        print("No overlapping dates found for correlation.")
        return None, None

    # Simple Linear Regression: y = mx + c
    n = len(x_vals)
    sum_x = sum(x_vals)
    sum_y = sum(y_vals)
    sum_xy = sum(x*y for x, y in zip(x_vals, y_vals))
    sum_xx = sum(x*x for x in x_vals)
    
    slope = (n * sum_xy - sum_x * sum_y) / (n * sum_xx - sum_x**2)
    intercept = (sum_y - slope * sum_x) / n
    
    print(f"Correlation calculated on {n} overlapping data points (Oct-Dec 2025).")
    print(f"Formula: PercentFull = {slope:.4f} * WaitTime + {intercept:.4f}")
    
    return slope, intercept

def convert_files(slope, intercept):
    """Iterates through JSON files and updates old metric values."""
    files = glob.glob(os.path.join(DATA_DIR, "crowd_info-*.json"))
    
    count = 0
    for file_path in files:
        # Extract date from filename: crowd_info-YYYYMMDD.json
        filename = os.path.basename(file_path)
        try:
            date_part = filename.replace("crowd_info-", "").replace(".json", "")
            file_date_int = int(date_part)
        except ValueError:
            continue
            
        # Only process files gathered on or before the switch
        if file_date_int <= SWITCH_DATE_INT:
            with open(file_path, 'r') as f:
                data = json.load(f)
            
            modified = False
            for entry in data:
                old_val = entry.get('crowd_info')
                if old_val is not None:
                    # Apply conversion
                    new_val = slope * old_val + intercept
                    # Cap at 100 and floor at 0 just in case
                    new_val = max(0, min(100, new_val))
                    
                    # Update the entry
                    entry['crowd_info'] = int(round(new_val))
                    modified = True
            
            if modified:
                with open(file_path, 'w') as f:
                    json.dump(data, f, indent=2)
                print(f"Updated: {filename}")
                count += 1
                
    print(f"Total files updated: {count}")

def main():
    wait_times = parse_wait_times(raw_wait_data)
    
    # Path to the file that definitely has the NEW metric
    ref_file_path = os.path.join(DATA_DIR, NEW_METRIC_REF_FILE)
    
    slope, intercept = calculate_correlation(wait_times, ref_file_path)
    
    if slope is not None:
        convert_files(slope, intercept)

if __name__ == "__main__":
    main()
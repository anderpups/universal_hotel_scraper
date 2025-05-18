import glob
import json
import os
import pandas
import matplotlib
import matplotlib.pyplot as plt

data_folder = "data"
index_file = os.path.join(data_folder, "index.html")
index_html = """
<html>
<head>
<title>Universal Hotel Info</title>
<link rel="stylesheet" href="style.css">
</head>
<h1>Universal Hotel Info</h1>
<body>
"""

bottom_of_html = """
    <script>
    $(document).ready(function() {
        $('#T_1e83b').DataTable({
            scrollX: true,
            dom: 'Bfrtip',
            buttons: [
                'colvis'
            ],
            pageLength: 30,
            // Optional: initial sorting, e.g. by date
            // "order": [[0, "asc"]]
        });
    });
    </script>
    <script>
    // Custom filtering function for date range
    $.fn.dataTable.ext.search.push(
    function(settings, data, dataIndex) {
        // Get the value from the first column (row header, date)
        var dateStr = $(settings.aoData[dataIndex].nTr).find('th').text();
        if (!dateStr) return true; // skip if no date

        // Parse the date in MM/DD/YY format
        var parts = dateStr.split('/');
        var rowDate = new Date('20' + parts[2], parts[0] - 1, parts[1]); // e.g. 05/17/25

        var min = $('#min-date').val();
        var max = $('#max-date').val();

        var minDate = min ? new Date(min) : null;
        var maxDate = max ? new Date(max) : null;

        // Remove time part for comparison
        rowDate.setHours(0,0,0,0);
        if (minDate) minDate.setHours(0,0,0,0);
        if (maxDate) maxDate.setHours(0,0,0,0);

        if (
        (!minDate || rowDate >= minDate) &&
        (!maxDate || rowDate <= maxDate)
        ) {
        return true;
        }
        return false;
    }
    );

    $(document).ready(function() {
        var table;
        if (!$.fn.DataTable.isDataTable('#T_1e83b')) {
            table = $('#T_1e83b').DataTable({
                scrollX: true,
                dom: 'Bfrtip',
                buttons: [
                    'colvis'
                ],
                pageLength: 30,
                // "order": [[0, "asc"]]
            });
        } else {
            table = $('#T_1e83b').DataTable();
        }

        // Event listeners for the date inputs
        $('#min-date, #max-date').on('change', function() {
            table.draw();
        });
    });
    </script>
    </body>
  """

all_data = []

# Find all JSON files in the data folder
json_files = glob.glob(os.path.join(data_folder, "hotel_info*.json"))

def format_price(price):
    """Format the price to include a dollar sign """
    try:
        return f"${int(price)}"
    except ValueError:
        return "N/A"

def color_gradient(s, color_list=['#00ff00', '#ffff00', '#ff0000']):
    """
    Applies a smooth color gradient to a Pandas Series,
    using matplotlib for more colors between the ends.
    color_list: list of hex colors for the gradient stops.
    """
    max_val = s.max()
    min_val = s.min()
    if max_val == min_val:
        normalized = pandas.Series([0.5] * len(s), index=s.index)
    else:
        normalized = (s - min_val) / (max_val - min_val)

    cmap = matplotlib.colors.LinearSegmentedColormap.from_list("custom_gradient", color_list)

    def get_color(val):
        if pandas.isna(val):
            return 'background-color: DarkGray'
        r, g, b, _ = [int(x * 255) for x in cmap(val)]
        return f'background-color: rgb({r},{g},{b})'

    return normalized.apply(get_color)

for file_path in json_files:
    with open(file_path, "r") as f:
        data = json.load(f)
        filename = os.path.basename(file_path)
        gather_date = filename.split("-")[1].split(".")[0]
    df = pandas.DataFrame(data)
    pivot_df = df.pivot_table(index='date', columns='name', values='price')
    
    pivot_df.index = pandas.to_datetime(pivot_df.index, format='%m/%d/%y')
    pivot_df = pivot_df.sort_index()
    
    with open(f'{data_folder}/crowd_info-{gather_date}.json', "r") as f:
        crowd_info = json.load(f)
    crowd_info_series = pandas.Series(
        [item['crowd_info'] for item in crowd_info],
        index=[item['date'] for item in crowd_info]
    )
    crowd_info_series.index = pandas.to_datetime(crowd_info_series.index, format='%m/%d/%y')
    ## Add the crowd info to the pivot_df
    pivot_df.insert(0, 'Crowd', crowd_info_series)

    # pivot_df['crowd_info'] = crowd_info_series
    ## Get the Day from the date and add it to the pivot_df
    day = pandas.to_datetime(pivot_df.index, format='%m/%d/%y').strftime('%a')
    
    pivot_df.insert(0, 'Day', day)
    
    ## Format the index to be the date in the format of mm/dd/yy
    pivot_df.index = pandas.to_datetime(pivot_df.index, format='%m/%d/%y').strftime('%m/%d/%y')

    # Apply color gradient and format each cell that is a price
    for col in pivot_df.columns:
        if col not in ['Day', 'Crowd']:
            styles = color_gradient(pivot_df[col])
            pivot_df[col] = [
                f'<div style="{style}">{format_price(val)}</div>'
                for style, val in zip(styles, pivot_df[col])
            ]

    # Setting gradient color for the 'Crowd' column
    styles = color_gradient(pivot_df['Crowd'])
    pivot_df['Crowd'] = [
        f'<div style="{style}">{val}</div>'
        for style, val in zip(styles, pivot_df['Crowd'])
    ]

    ## Remove the index and columns names
    pivot_df.index.name = None
    pivot_df.columns.name = None

    styled_table = pivot_df.style.set_sticky(axis="columns")
    
    ## Set the style of the column headers
    header_style = """
    <head>
    <title>Universal Hotel Info</title>
    <!-- DataTables CSS -->
    <link rel="stylesheet" href="https://cdn.datatables.net/1.13.7/css/jquery.dataTables.min.css">
    <!-- jQuery -->
    <script src="https://code.jquery.com/jquery-3.7.1.min.js"></script>
    <!-- DataTables JS -->
    <script src="https://cdn.datatables.net/1.13.7/js/jquery.dataTables.min.js"></script>
    <!-- DataTables ColVis extension for column hiding -->
    <link rel="stylesheet" href="https://cdn.datatables.net/buttons/2.4.1/css/buttons.dataTables.min.css">
    <script src="https://cdn.datatables.net/buttons/2.4.1/js/dataTables.buttons.min.js"></script>
    <script src="https://cdn.datatables.net/buttons/2.4.1/js/buttons.colVis.min.js"></script>
    <style>
    thead th {
        background-color: #f8f8f8 !important;
        color: #222 !important;
        position: sticky;
        top: 0;
        z-index: 3;
    }
    </style>
    <style>
    .dataTables_filter {
    display: none !important;
    }
    </style>
    <div style="height:1000px; width:1200px; overflow:auto; border:1px solid #ccc;">
    <style type="text/css">

    #T_1e83b thead tr:nth-child(1) th {
    position: sticky;
    background-color: inherit;
    top: 0px;
    z-index: 2;
    }
    </style>

    </head>
    <body>
    <div style="margin-bottom: 10px;">
    <label for="min-date">Start date:</label>
    <input type="date" id="min-date">
    <label for="max-date" style="margin-left:10px;">End date:</label>
    <input type="date" id="max-date">
    </div>
    """

    ## Set the table to scrollable
    html_table = styled_table.to_html(index_names=False, escape=False, table_id="hotel-info")
    scrollable_html = f"""
    {header_style}
    <div style="height:1000px; width:1000px; overflow:auto; border:1px solid #ccc;">
    {html_table}
    </div>
    {bottom_of_html}
    """
    with open(f"{data_folder}/hotel_info-{gather_date}.html", "w") as f:
        f.write(scrollable_html) 
    
    index_html += f'<a href="hotel_info-{gather_date}.html">Data for {gather_date}</a><br>\n'

index_html += "</ul>\n</body></html>"
# Write to index.html
with open(index_file, "w") as f:
    f.write(index_html)
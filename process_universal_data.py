import glob
import json
import os
import pandas
import matplotlib
import matplotlib.pyplot as plt

data_folder = "data"
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
        gather_date = os.path.basename(file_path).split("-")[1].split(".")[0]
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
    <style>
    thead th {
        background-color: #f8f8f8 !important;
        color: #222 !important;
        position: sticky;
        top: 0;
        z-index: 3;
    }
    </style>
    """

    ## Set the table to scrollable
    html_table = styled_table.to_html( index_names=False, escape=False)
    scrollable_html = f"""
    {header_style}
    <div style="height:1000px; width:1200px; overflow:auto; border:1px solid #ccc;">
    {html_table}
    </div>
    """
    with open(f"{data_folder}/hotel_info-{gather_date}.html", "w") as f:
        f.write(scrollable_html)
 

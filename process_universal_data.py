import glob
import json
import os
import pandas

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

def color_gradient(s, color1='#00ff00', color2='#ff0000'):
    """
    Applies a green to red color gradient to a Pandas Series,
    where the maximum value is mapped to red.

    Args:
        s (pd.Series): The Pandas Series to style.
        color1 (str, optional): The color for the minimum value. Defaults to 'green'.
        color2 (str, optional): The color for the maximum value. Defaults to 'red'.

    Returns:
        pd.Series: A Series of strings with the CSS styling.
    """
    max_val = s.max()
    min_val = s.min()  # Get the minimum value for scaling

    if max_val == min_val:
        # Handle the case where all values are the same
        normalized = pandas.Series([0.5] * len(s), index=s.index)  # All values in the middle
    else:
        normalized = (s - min_val) / (max_val - min_val)  # Normalize to range 0-1

    r1, g1, b1 = int(color1[1:3], 16), int(color1[3:5], 16), int(color1[5:7], 16)
    r2, g2, b2 = int(color2[1:3], 16), int(color2[3:5], 16), int(color2[5:7], 16)

    def get_color(val):
        if pandas.isna(val):
            return 'background-color: LightGray'
        r = int(r1 + (r2 - r1) * val)
        g = int(g1 + (g2 - g1) * val)
        b = int(b1 + (b2 - b1) * val)
        return f'background-color: rgb({r},{g},{b})'

    return normalized.apply(get_color)

# def set_highlight(cell):
#     isna = True if cell == 'N/A' else False
#     return ['background-color: LightGray' if isna else '']

for file_path in json_files:
    with open(file_path, "r") as f:
        data = json.load(f)
        gather_date = os.path.basename(file_path).split("-")[1].split(".")[0]
    df = pandas.DataFrame(data)
    pivot_df = df.pivot_table(index='date', columns='name', values='price')
    
    pivot_df.index = pandas.to_datetime(pivot_df.index, format='%m/%d/%y')
    pivot_df = pivot_df.sort_index()

    ## Format the price columns
    for col in pivot_df.columns:
        pivot_df[col] = pivot_df[col].apply(format_price)
    
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
    for col in pivot_df.columns:
        if col not in ['Day', 'Crowd']:
            # Remove $ and convert to float, set errors='coerce' to turn 'N/A' into NaN
            pivot_df[col] = pandas.to_numeric(
                pivot_df[col].replace('[\$,]', '', regex=True),
                errors='coerce'
            )
    # Apply color gradient column-wise and format each cell
    for col in pivot_df.columns:
        if col not in ['Day', 'Crowd']:
            styles = color_gradient(pivot_df[col])
            pivot_df[col] = [
                f'<div style="{style}">{format_price(val)}</div>'
                for style, val in zip(styles, pivot_df[col])
            ]

    # If you want to style 'Crowd' column as well, do the same:
    styles = color_gradient(pivot_df['Crowd'])
    pivot_df['Crowd'] = [
        f'<div style="{style}">{val}</div>'
        for style, val in zip(styles, pivot_df['Crowd'])
    ]

    ## Create html file
    pivot_df.to_html(f"{data_folder}/hotel_info-{gather_date}.html", index_names=False, escape=False)

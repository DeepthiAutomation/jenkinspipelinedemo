
import dash
from dash import html, dcc
from dash.dependencies import Input, Output
import pandas as pd
import os

# Initialize the Dash app
app = dash.Dash(__name__)

# Function to read CSV data
def read_csv_data(csv_path):
    try:
        df = pd.read_csv(csv_path)
        return df
    except Exception as e:
        print(f"Error reading CSV: {e}")
        return pd.DataFrame()

# Function to get dropdown options from CSV data
def get_dropdown_options(csv_data):
    if not csv_data.empty:
        dropdown_options = [{'label': row, 'value': row} for row in csv_data.columns]
        return dropdown_options
    else:
        return []

# Define layout of the app
app.layout = html.Div(
    style={'textAlign': 'center', 'padding': '50px'},
    children=[
        html.H1('CSV Data Viewer'),
        dcc.Dropdown(
            id='csv-dropdown',
            placeholder='Select a column',
            style={'width': '50%', 'margin': 'auto', 'margin-bottom': '20px'}
        ),
        html.Div(id='csv-data-container')
    ]
)

# Callback to populate dropdown options
@app.callback(
    Output('csv-dropdown', 'options'),
    [Input('interval-component', 'n_intervals')]  # Add any other input triggers as needed
)
def update_dropdown_options(n_intervals):
    # Read CSV data
    csv_path = 'your_csv_file.csv'  # Specify the path to your CSV file
    csv_data = read_csv_data(csv_path)
    # Get dropdown options from CSV data
    dropdown_options = get_dropdown_options(csv_data)
    return dropdown_options

# Run the app
if __name__ == '__main__':
    app.run_server(debug=True)

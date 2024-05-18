import dash
from dash import html, dcc
from dash.dependencies import Input, Output
import os

# Initialize the Dash app
app = dash.Dash(__name__)

# Function to get available CSV files in the directory
def get_available_csv_files(directory):
    return [file for file in os.listdir(directory) if file.endswith('.csv')]

# Define layout of the app
app.layout = html.Div(
    style={'textAlign': 'center', 'padding': '50px'},
    children=[
        html.H1('CSV Data Viewer'),
        dcc.Dropdown(
            id='csv-dropdown',
            placeholder='Select a CSV file',
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
    # Get available CSV files
    available_csv_files = get_available_csv_files('csv_directory')
    dropdown_options = [{'label': file, 'value': file} for file in available_csv_files]
    return dropdown_options

# Run the app
if __name__ == '__main__':
    app.run_server(debug=True)

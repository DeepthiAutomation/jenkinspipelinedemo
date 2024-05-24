import dash
from dash import dcc, html, Input, Output
import dash_table
import dash_bootstrap_components as dbc
import requests
import pandas as pd

# Initialize the Dash app
app = dash.Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])

# Define a function to fetch data from an API
def fetch_data():
    url = "https://api.example.com/data"  # Replace with your API URL
    response = requests.get(url)
    if response.status_code == 200:
        return response.json()
    else:
        return []

# Function to convert fetched data into a DataFrame
def process_data(data):
    df = pd.DataFrame(data)
    return df

# Define the layout of the app
app.layout = html.Div([
    dbc.Button("Fetch Data", id='fetch-button', n_clicks=0),
    dcc.Dropdown(id='dropdown-1', options=[], value=None),
    dcc.Dropdown(id='dropdown-2', options=[], value=None),
    dash_table.DataTable(id='table', columns=[])
])

# Callback to update dropdowns and table when data is fetched
@app.callback(
    Output('dropdown-1', 'options'),
    Output('dropdown-1', 'value'),
    Output('dropdown-2', 'options'),
    Output('dropdown-2', 'value'),
    Output('table', 'columns'),
    Output('table', 'data'),
    Input('fetch-button', 'n_clicks')
)
def update_data(n_clicks):
    if n_clicks > 0:
        data = fetch_data()
        if data:
            df = process_data(data)
            dropdown_1_options = [{'label': item, 'value': item} for item in df['category'].unique()]
            columns = [{'name': col, 'id': col} for col in df.columns]
            return dropdown_1_options, dropdown_1_options[0]['value'], [], None, columns, df.to_dict('records')
    return [], None, [], None, [], []

# Callback to populate dropdown 2 based on dropdown 1 selection
@app.callback(
    Output('dropdown-2', 'options'),
    Output('dropdown-2', 'value'),
    Input('dropdown-1', 'value')
)
def set_dropdown_2_options(selected_category):
    if selected_category:
        data = fetch_data()
        df = process_data(data)
        filtered_df = df[df['category'] == selected_category]
        dropdown_2_options = [{'label': item, 'value': item} for item in filtered_df['subcategory'].unique()]
        return dropdown_2_options, dropdown_2_options[0]['value'] if dropdown_2_options else None
    return [], None

# Callback to filter table based on both dropdown selections
@app.callback(
    Output('table', 'data'),
    Input('dropdown-1', 'value'),
    Input('dropdown-2', 'value')
)
def filter_table(selected_category, selected_subcategory):
    data = fetch_data()
    df = process_data(data)
    if selected_category:
        df = df[df['category'] == selected_category]
    if selected_subcategory:
        df = df[df['subcategory'] == selected_subcategory]
    return df.to_dict('records')

# Run the app
if __name__ == '__main__':
    app.run_server(debug=True)

import dash
from dash import dcc, html, Input, Output
import dash_table
import requests
import pandas as pd

# Sample API endpoint
# This should be replaced with the actual API endpoint
API_URL = "https://api.example.com/data"

# Initialize the Dash app
app = dash.Dash(__name__)

# Layout of the app
app.layout = html.Div([
    dcc.Dropdown(
        id='category-dropdown',
        options=[{'label': 'Fruit', 'value': 'Fruit'}, {'label': 'Vegetable', 'value': 'Vegetable'}],
        placeholder="Select a category"
    ),
    dcc.Dropdown(
        id='item-dropdown',
        placeholder="Select an item"
    ),
    dash_table.DataTable(
        id='data-table',
        columns=[{'name': 'Category', 'id': 'Category'}, {'name': 'Item', 'id': 'Item'}],
        data=[],  # Initial empty data
        style_table={'overflowX': 'auto'}
    )
])

# Callback to update the second dropdown and table based on the first dropdown selection
@app.callback(
    [Output('item-dropdown', 'options'),
     Output('data-table', 'data')],
    Input('category-dropdown', 'value')
)
def update_item_dropdown_and_table(selected_category):
    if selected_category is None:
        return [], []

    # Fetch data from the API
    response = requests.get(API_URL, params={'category': selected_category})

    # Check if the response is valid
    if response.status_code != 200:
        return [], []

    # Convert the response JSON to a DataFrame
    data = response.json()
    df = pd.DataFrame(data)

    # Filter the DataFrame based on the selected category
    filtered_df = df[df['Category'] == selected_category]

    # Prepare dropdown options
    dropdown_options = [{'label': item, 'value': item} for item in filtered_df['Item']]

    # Prepare data for the table
    table_data = filtered_df.to_dict('records')

    return dropdown_options, table_data

# Run the app
if __name__ == '__main__':
    app.run_server(debug=True)

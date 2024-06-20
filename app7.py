import dash
from dash import dcc, html, Input, Output
import dash_table

# Initialize the Dash app
app = dash.Dash(__name__)

app.layout = html.Div([
    html.H1("Dash Table Example"),
    html.Button("Load Data", id="load-data-button", n_clicks=0),
    dash_table.DataTable(
        id='table',
        columns=[
            {"name": "Name", "id": "Name"},
            {"name": "Age", "id": "Age"},
            {"name": "City", "id": "City"}
        ],
        data=[],
        style_table={'width': '50%'},
        style_cell={'textAlign': 'left'},
    )
])

@app.callback(
    Output('table', 'data'),
    [Input('load-data-button', 'n_clicks')]
)
def update_table(n_clicks):
    if n_clicks > 0:
        # Simulate fetching raw data (list of lists)
        raw_data = [
            ["Alice", 30, "New York"],
            ["Bob", 24, "San Francisco"],
            ["Charlie", 29, "Chicago"]
        ]
        # Column headers
        columns = ["Name", "Age", "City"]
        # Convert list of lists to list of dictionaries
        data_dict = [dict(zip(columns, row)) for row in raw_data]
        return data_dict
    return []

if __name__ == '__main__':
    app.run_server(debug=True)

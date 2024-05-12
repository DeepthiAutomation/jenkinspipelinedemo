import dash
from dash import dcc, html, Output, Input, State
import pandas as pd
from dash.exceptions import PreventUpdate
import io
import base64

app = dash.Dash(__name__)

app.layout = html.Div([
    html.Button("Generate Row", id="generate-row-btn"),
    dcc.Store(id="csv-store"),
    html.Div(id="csv-output")
])

@app.callback(
    Output("csv-store", "data"),
    [Input("generate-row-btn", "n_clicks")],
    [State("csv-store", "data")]
)
def generate_row(n_clicks, csv_data):
    if not n_clicks:
        raise PreventUpdate
    
    # Generate dummy row (you can replace this with your own data)
    row_data = ["John", 30, "New York"]  # Assuming a list of values for each row
    
    # Initialize CSV data if it doesn't exist
    if not csv_data:
        csv_data = []
    
    # Append row to CSV data
    csv_data.append(row_data)
    
    return csv_data

@app.callback(
    Output("csv-output", "children"),
    [Input("csv-store", "data")]
)
def process_csv(csv_data):
    if not csv_data:
        raise PreventUpdate
    
    # Convert list of lists to DataFrame
    df = pd.DataFrame(csv_data, columns=["Name", "Age", "City"])
    
    # Process DataFrame (e.g., display in a DataTable)
    table = html.Table([
        html.Thead(html.Tr([html.Th(col) for col in df.columns])),
        html.Tbody([
            html.Tr([
                html.Td(df.iloc[i][col]) for col in df.columns
            ]) for i in range(len(df))
        ])
    ])
    
    return table

if __name__ == "__main__":
    app.run_server(debug=True)

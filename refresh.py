import dash
from dash import html
from dash.dependencies import Output, Input
import pandas as pd
import time

app = dash.Dash(__name__)

# Load initial CSV data
df = pd.read_csv('data.csv')

app.layout = html.Div([
    html.H1("CSV File Refresh Example"),
    html.Div(id='live-update-text'),
    dcc.Interval(
        id='interval-component',
        interval=5*60*1000,  # in milliseconds (5 minutes)
        n_intervals=0
    )
])

# Callback to update data
@app.callback(
    Output('live-update-text', 'children'),
    [Input('interval-component', 'n_intervals')]
)
def update_data(n):
    # Reload CSV file
    global df
    df = pd.read_csv('data.csv')
    
    # Optionally, process or manipulate the data here if needed
    
    # Update Dash app layout or components with new data
    return f"Data last refreshed at: {time.strftime('%Y-%m-%d %H:%M:%S')}"

if __name__ == '__main__':
    app.run_server(debug=True)

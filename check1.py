import dash
from dash import html, dcc
from dash.dependencies import Input, Output
import pandas as pd
import schedule
import threading
import time

# Function to generate CSV data
def generate_csv():
    # Your code to generate CSV data
    # For demonstration, let's create a DataFrame with dummy data
    data = {
        'Name': ['Alice', 'Bob', 'Charlie'],
        'Age': [25, 30, 35]
    }
    df = pd.DataFrame(data)
    df.to_csv('data.csv', index=False)

# Function to read CSV data
def read_csv_data():
    try:
        df = pd.read_csv('data.csv')
        return df.to_dict('records')
    except Exception as e:
        print(f"Error reading CSV: {e}")
        return []

# Initialize the Dash app
app = dash.Dash(__name__)

# Define layout of the app
app.layout = html.Div(
    style={'textAlign': 'center', 'padding': '50px'},
    children=[
        html.H1('CSV Data Viewer'),
        html.Div(id='csv-data-container'),
        dcc.Interval(id='interval-component', interval=60000, n_intervals=0)  # Refresh every 60 seconds
    ]
)

# Define callback to update UI with CSV data
@app.callback(
    Output('csv-data-container', 'children'),
    Input('interval-component', 'n_intervals')
)
def update_csv_data(n_intervals):
    data = read_csv_data()
    if data:
        return html.Table([
            html.Thead([html.Tr([html.Th(col) for col in data[0].keys()])]),
            html.Tbody([
                html.Tr([
                    html.Td(data[i][col]) for col in data[0].keys()
                ]) for i in range(len(data))
            ])
        ])
    else:
        return html.Div('No data available.')

# Scheduler function to run generate_csv() every 5 minutes
def scheduler_thread():
    while True:
        schedule.run_pending()
        time.sleep(1)

# Start scheduler thread
scheduler_thread = threading.Thread(target=scheduler_thread)
scheduler_thread.daemon = True
scheduler_thread.start()

# Schedule generate_csv() function to run every 5 minutes
schedule.every(5).minutes.do(generate_csv)

# Run the app
if __name__ == '__main__':
    app.run_server(debug=True)

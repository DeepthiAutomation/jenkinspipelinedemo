import dash
from dash import html, dcc
from dash.dependencies import Input, Output
import pandas as pd
import schedule
import threading
import time

# Initialize the Dash app
app = dash.Dash(__name__)

# Function to generate or fetch CSV data dynamically
def get_dynamic_csv_data():
    # Replace this function with logic to generate or fetch CSV data dynamically
    # For example, you can fetch data from a database or API and convert it to a pandas DataFrame
    # For demonstration purposes, let's create a DataFrame with dummy data
    data = {
        'Key': ['JIRA-1', 'JIRA-2', 'JIRA-3'],
        'Summary': ['Dummy summary 1', 'Dummy summary 2', 'Dummy summary 3'],
        'Assignee': ['User 1', 'User 2', 'User 3'],
        'Status': ['Open', 'In Progress', 'Resolved'],
        'Sprint': ['Sprint 1', 'Sprint 2', 'Sprint 3'],
        'Story Points': [3, 5, 8],
        'Epic Link': ['Epic-1', 'Epic-2', 'Epic-3']
    }
    df = pd.DataFrame(data)
    return df

# Define the layout of the app
app.layout = html.Div(
    style={'textAlign': 'center', 'padding': '50px'},
    children=[
        html.Div(id='jira-data-container'),
        dcc.Interval(id='interval-component', interval=60000, n_intervals=0),  # Refresh every 60 seconds
    ]
)

# Define callback to update UI
@app.callback(
    Output('jira-data-container', 'children'),
    Input('interval-component', 'n_intervals')
)
def update_data(n_intervals):
    # Get dynamic CSV data
    df = get_dynamic_csv_data()
    # Update UI with data
    return html.Div([
        html.H1('Jira Open Sprints with Label'),
        html.Table([
            html.Thead(html.Tr([html.Th(col) for col in df.columns])),
            html.Tbody([
                html.Tr([
                    html.Td(df.iloc[i][col]) for col in df.columns
                ]) for i in range(len(df))
            ])
        ])
    ])

# Run the app
if __name__ == '__main__':
    app.run_server(debug=True)

import dash
from dash import dcc, html, Input, Output
import requests

app = dash.Dash(__name__)

# Define your APIs to check
APIs = [
    {"name": "API 1", "url": "http://api1.example.com/health"},
    {"name": "API 2", "url": "http://api2.example.com/health"},
    # Add more APIs as needed
]

def check_api_health(api):
    try:
        response = requests.get(api['url'])
        if response.status_code == 200:
            return True
        else:
            return False
    except Exception as e:
        print(f"Error checking {api['name']} - {e}")
        return False

app.layout = html.Div([
    html.H1("API Health Check Dashboard"),
    dcc.Graph(id='health-graph'),
    dcc.Interval(
        id='interval-component',
        interval=60*1000,  # in milliseconds
        n_intervals=0
    )
])

@app.callback(Output('health-graph', 'figure'), [Input('interval-component', 'n_intervals')])
def update_graph(n):
    api_names = []
    api_statuses = []
    for api in APIs:
        api_names.append(api['name'])
        status = "Healthy" if check_api_health(api) else "Unhealthy"
        api_statuses.append(status)

    data = [{
        'x': api_names,
        'y': api_statuses,
        'type': 'bar',
        'name': 'API Health Status'
    }]

    layout = {
        'title': 'API Health Status'
    }

    return {'data': data, 'layout': layout}

if __name__ == '__main__':
    app.run_server(debug=True)

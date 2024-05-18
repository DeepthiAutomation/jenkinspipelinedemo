import dash
from dash import dcc, html
import dash_table
import pandas as pd

# Sample data
data = {
    'Assignee': ['Alice', 'Bob', 'Alice', 'Bob', 'Charlie', 'Alice'],
    'Status': ['Open', 'In Progress', 'Open', 'Closed', 'Open', 'Closed'],
    'StoryPoints': [5, 3, 8, 2, 13, 1]
}

df = pd.DataFrame(data)

# Initialize Dash app
app = dash.Dash(__name__)

# App layout
app.layout = html.Div([
    html.H1("Jira Dashboard", style={'textAlign': 'center'}),
    dash_table.DataTable(
        id='table',
        columns=[{"name": i, "id": i} for i in df.columns],
        data=df.to_dict('records'),
        style_data_conditional=[
            {
                'if': {
                    'filter_query': '{StoryPoints} > 10',
                    'column_id': 'StoryPoints'
                },
                'backgroundColor': 'tomato',
                'color': 'white'
            },
            {
                'if': {
                    'filter_query': '{StoryPoints} <= 10',
                    'column_id': 'StoryPoints'
                },
                'backgroundColor': 'green',
                'color': 'white'
            }
        ],
        style_table={'overflowX': 'auto'}
    )
])

# Run the app
if __name__ == '__main__':
    app.run_server(debug=True)

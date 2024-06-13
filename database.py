import dash
import dash_core_components as dcc
import dash_html_components as html
import dash_table
from dash.dependencies import Input, Output, State
import requests
import sqlite3
import pandas as pd
import dash_bootstrap_components as dbc

# Initialize the Dash app
app = dash.Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])
server = app.server  # Expose the server variable for gunicorn

# Fetch projects from the database
def get_projects():
    conn = sqlite3.connect('jira_dashboard.db')
    df = pd.read_sql_query('SELECT DISTINCT project_name FROM projects', conn)
    conn.close()
    return df['project_name'].tolist()

app.layout = html.Div([
    html.H1("JIRA Dashboard"),
    
    html.Label("Select Projects:"),
    dcc.Dropdown(
        id='project-dropdown',
        options=[{'label': project, 'value': project} for project in get_projects()],
        multi=True
    ),
    
    html.Label("Enter Labels (comma separated):"),
    dcc.Input(id='label-input', type='text', value=''),
    
    html.Button('Get Stories', id='get-stories-button', n_clicks=0),
    
    dash_table.DataTable(
        id='stories-table',
        columns=[{'name': 'Story Key', 'id': 'key'}, {'name': 'Summary', 'id': 'summary'}],
        data=[]
    )
])

@app.callback(
    Output('stories-table', 'data'),
    [Input('get-stories-button', 'n_clicks')],
    [State('project-dropdown', 'value'), State('label-input', 'value')]
)
def get_stories(n_clicks, projects, labels_input):
    if n_clicks == 0:
        return []
    
    if not projects:
        return []
    
    # Parse the labels input
    labels = [label.strip() for label in labels_input.split(',') if label.strip()]
    
    # Generate JQL query
    jql = ' AND '.join([f'project = "{project}"' for project in projects])
    if labels:
        jql += ' AND ' + ' AND '.join([f'labels = "{label}"' for label in labels])
    jql += ' AND status = "Open" AND sprint in openSprints()'
    
    # Fetch stories from JIRA
    stories = []
    for jira_url in jira_urls:
        search_url = f'{jira_url}/rest/api/2/search'
        response = requests.get(search_url, params={'jql': jql}, auth=auth)
        issues = response.json().get('issues', [])
        for issue in issues:
            stories.append({
                'key': issue['key'],
                'summary': issue['fields']['summary']
            })
    
    return stories

if __name__ == '__main__':
    app.run_server(debug=True)

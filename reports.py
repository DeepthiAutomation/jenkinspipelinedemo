import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output, State
import dash_table
import plotly.express as px
import pandas as pd
import dash_bootstrap_components as dbc
import sqlite3
import requests
from flask_caching import Cache
import json

# Initialize the Dash app
app = dash.Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP], suppress_callback_exceptions=True)
server = app.server

# Setup cache
cache = Cache(app.server, config={
    'CACHE_TYPE': 'simple',  # or 'redis', 'filesystem', etc.
    'CACHE_DEFAULT_TIMEOUT': 300  # 5 minutes
})

# Authentication for JIRA (replace with your credentials)
auth = ('username', 'password')

# Fetch projects from the database
def get_projects():
    conn = sqlite3.connect('jira_dashboard.db')
    df = pd.read_sql_query('SELECT url, project_id, project_name FROM projects', conn)
    conn.close()
    return df

projects_df = get_projects()

# Function to fetch data from JIRA and cache it
@cache.memoize()
def fetch_sprint_data(jira_url, jql):
    response = requests.get(f'{jira_url}/rest/api/2/search?jql={jql}&fields=summary,assignee,storyPoints,sprint', auth=auth)

    if response.status_code != 200:
        raise Exception(f'Failed to fetch data: {response.content}')
    
    issues = response.json()['issues']
    sprint_data = []

    for issue in issues:
        fields = issue['fields']
        sprint_data.append({
            'sprint': fields['sprint']['name'] if 'sprint' in fields else 'No Sprint',
            'story_points': fields['storyPoints'] if 'storyPoints' in fields else 0,
            'assignee': fields['assignee']['displayName'] if 'assignee' in fields else 'Unassigned',
            'project': fields['project']['name'] if 'project' in fields else 'No Project'
        })
    
    return pd.DataFrame(sprint_data)

# Function to save JQL query to the database
def save_jql_query(name, jql):
    conn = sqlite3.connect('jira_dashboard.db')
    cursor = conn.cursor()
    cursor.execute("INSERT OR REPLACE INTO jql_queries (name, jql) VALUES (?, ?)", (name, jql))
    conn.commit()
    conn.close()

# Function to load JQL query from the database
def load_jql_query(name):
    conn = sqlite3.connect('jira_dashboard.db')
    cursor = conn.cursor()
    cursor.execute("SELECT jql FROM jql_queries WHERE name = ?", (name,))
    query = cursor.fetchone()
    conn.close()
    return query[0] if query else None

# Function to get all saved JQL queries from the database
def get_all_jql_queries():
    conn = sqlite3.connect('jira_dashboard.db')
    cursor = conn.cursor()
    cursor.execute("SELECT name FROM jql_queries")
    queries = cursor.fetchall()
    conn.close()
    return [{'label': query[0], 'value': query[0]} for query in queries]

# Home Page Layout
home_layout = html.Div([
    html.H1("Welcome to JIRAView360", style={'textAlign': 'center', 'fontFamily': 'Arial, sans-serif'}),
    html.Div([
        dcc.Link('Get Stories', href='/stories', className='btn btn-success', style={'marginRight': '10px'}),
        dcc.Link('Get Backlogs', href='/backlogs', className='btn btn-success', style={'marginRight': '10px'}),
        dcc.Link('Bulk Create Stories', href='/bulk-create', className='btn btn-success', style={'marginRight': '10px'}),
        dcc.Link('Get Reports Dashboard', href='/reports-dashboard', className='btn btn-success')
    ], style={'textAlign': 'center', 'padding': '20px'})
])

# Bulk Create Stories Page Layout (Assumed already defined)
bulk_create_layout = html.Div([
    html.H1("Bulk Create Stories", style={'textAlign': 'center', 'fontFamily': 'Arial, sans-serif'}),
    html.Div([
        html.Label("Select Project:"),
        dcc.Dropdown(
            id='project-dropdown',
            options=[{'label': row['project_name'], 'value': row['project_id']} for _, row in projects_df.iterrows()]
        ),
        html.Label("Epic Link:"),
        dcc.Input(id='epic-input', type='text', value=''),
        html.Label("Sprint:"),
        dcc.Input(id='sprint-input', type='text', value=''),
        html.Label("Labels (comma-separated):"),
        dcc.Input(id='label-input', type='text', value=''),
        html.Label("Story Summaries (one per line):"),
        dcc.Textarea(id='summaries-input', style={'width': '100%', 'height': '200px'}),
        html.Button('Create Stories', id='create-stories-button', n_clicks=0, className='btn btn-success', style={'marginTop': '10px'}),
        html.Div(id='creation-result', style={'marginTop': '20px'})
    ], style={'padding': '20px'}),
    html.Div([
        dcc.Link('Back to Home', href='/', className='btn btn-secondary', style={'marginTop': '10px'})
    ], style={'textAlign': 'center'})
])

# Reports Dashboard Layout
reports_dashboard_layout = html.Div([
    html.H1("Reports Dashboard", style={'textAlign': 'center', 'fontFamily': 'Arial, sans-serif'}),
    
    html.Div([
        html.Button('Get Backlogs', id='get-backlogs-button', n_clicks=0, className='btn btn-success', style={'marginBottom': '20px'}),
        html.Button('Save JQL', id='save-jql-button', n_clicks=0, className='btn btn-primary', style={'marginLeft': '10px'}),
        dcc.Input(id='jql-name-input', type='text', placeholder='Enter JQL name', style={'marginLeft': '10px'}),
        dcc.Input(id='jql-input', type='text', placeholder='Enter JQL query', style={'marginLeft': '10px', 'width': '40%'}),
        dcc.Dropdown(id='jql-dropdown', options=get_all_jql_queries(), placeholder='Select a JQL query', style={'marginLeft': '10px', 'marginTop': '10px'}),
        dcc.Dropdown(id='assignee-dropdown', multi=True, placeholder='Select Assignees', style={'marginLeft': '10px', 'marginTop': '10px'}),
    ], style={'textAlign': 'center'}),
    
    html.Div([
        dcc.Graph(id='sprint-storypoints-bar', style={'display': 'none'}),
        dcc.Graph(id='assignee-storypoints-bar', style={'display': 'none'}),
        dcc.Graph(id='project-storypoints-pie', style={'display': 'none'})
    ], className='row'),

    html.Div([
        dcc.Link('Back to Home', href='/', className='btn btn-secondary', style={'marginTop': '10px'})
    ], style={'textAlign': 'center'})
])

# Define the layout with a location component for routing
app.layout = html.Div([
    dcc.Location(id='url', refresh=False),
    html.Div(id='page-content')
])

# Update page content based on URL
@app.callback(Output('page-content', 'children'), [Input('url', 'pathname')])
def display_page(pathname):
    if pathname == '/stories':
        return stories_layout
    elif pathname == '/backlogs':
        return backlogs_layout
    elif pathname == '/bulk-create':
        return bulk_create_layout
    elif pathname == '/reports-dashboard':
        return reports_dashboard_layout
    else:
        return home_layout

# Callback to update the reports dashboard
@app.callback(
    [Output('sprint-storypoints-bar', 'figure'),
     Output('assignee-storypoints-bar', 'figure'),
     Output('project-storypoints-pie', 'figure'),
     Output('sprint-storypoints-bar', 'style'),
     Output('assignee-storypoints-bar', 'style'),
     Output('project-storypoints-pie', 'style'),
     Output('jql-dropdown', 'options'),
     Output('assignee-dropdown', 'value')],
    [Input('get-backlogs-button', 'n_clicks'),
     Input('jql-dropdown', 'value'),
     Input('save-jql-button', 'n_clicks')],
    [State('jql-name-input', 'value'),
     State('jql-input', 'value'),
     State('assignee-dropdown', 'value')]
)
def update_reports_dashboard(get_backlogs_clicks, selected_jql, save_jql_clicks, jql_name, jql_query, assignees):
    ctx = dash.callback_context

    if not ctx.triggered:
        return {}, {}, {}, {'display': 'none'}, {'display': 'none'}, {'display': 'none'}, get_all_jql_queries(), []

    button_id = ctx.triggered[0]['prop_id'].split('.')[0]

    if button_id == 'jql-dropdown' and selected_jql:
        jql_query = load_jql_query(selected_jql)
    else:
        n_clicks = get_backlogs_clicks

    if jql_query and n_clicks > 0:
        jira_url = 'YOUR_JIRA_URL'  # Replace with your JIRA instance URL
        sprint_data = fetch_sprint_data(jira_url, jql_query)

        if assignees:
            sprint_data = sprint_data[sprint_data['assignee'].isin(assignees)]

        df_sprint = sprint_data.groupby('sprint').sum().reset_index()
        df_assignee = sprint_data.groupby('assignee').sum().reset_index()
        df_project = sprint_data.groupby('project').sum().reset_index()

        # Create bar chart for Sprint vs Story Points
        sprint_storypoints_fig = px.bar(df_sprint, x='sprint', y='story_points', title='Sprint vs Story Points')

        # Create bar chart for Assignee vs Story Points
        assignee_storypoints_fig = px.bar(df_assignee, x='assignee', y='story_points', title='Assignee vs Story Points')

        # Create pie chart for Project vs Sum of Story Points
        project_storypoints_pie_fig = px.pie(df_project, names='project', values='story_points', title='Project vs Sum of Story Points')

        # Save the JQL query if 'Save JQL' button was clicked
        if button_id == 'save-jql-button' and jql_name and jql_query:
            save_jql_query(jql_name, jql_query)

        return sprint_storypoints_fig, assignee_storypoints_fig, project_storypoints_pie_fig, {'display': 'block'}, {'display': 'block'}, {'display': 'block'}, get_all_jql_queries(), assignees

    return {}, {}, {}, {'display': 'none'}, {'display': 'none'}, {'display': 'none'}, get_all_jql_queries(), []

if __name__ == '__main__':
    app.run_server(debug=True)

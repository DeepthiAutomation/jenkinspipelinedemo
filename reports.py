import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output, State
import plotly.express as px
import pandas as pd
import dash_bootstrap_components as dbc
import sqlite3

# Initialize the Dash app
app = dash.Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP], suppress_callback_exceptions=True)

# Authentication for JIRA (replace with your credentials)
auth = ('username', 'password')

# Fetch projects from the database
def get_projects():
    conn = sqlite3.connect('jira_dashboard.db')
    df = pd.read_sql_query('SELECT url, project_id, project_name FROM projects', conn)
    conn.close()
    return df

projects_df = get_projects()

# Home Page Layout
home_layout = html.Div([
    html.H1("Welcome to JIRA Dashboard", style={'textAlign': 'center', 'fontFamily': 'Arial, sans-serif'}),
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
        dcc.Graph(id='sprint-storypoints-bar'),
        dcc.Graph(id='assignee-storypoints-bar'),
        dcc.Graph(id='project-storypoints-pie')
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
     Output('project-storypoints-pie', 'figure')],
    [Input('url', 'pathname')]
)
def update_reports_dashboard(pathname):
    if pathname != '/reports-dashboard':
        return {}, {}, {}
    
    # Sample data - Replace with actual data fetching logic
    data = {
        'sprint': ['Sprint 1', 'Sprint 2', 'Sprint 3'],
        'story_points': [30, 40, 25],
        'assignee': ['Alice', 'Bob', 'Charlie'],
        'story_points_assignee': [35, 45, 30],
        'project': ['Project A', 'Project B', 'Project C'],
        'story_points_project': [50, 60, 40]
    }

    df_sprint = pd.DataFrame({
        'sprint': data['sprint'],
        'story_points': data['story_points']
    })

    df_assignee = pd.DataFrame({
        'assignee': data['assignee'],
        'story_points': data['story_points_assignee']
    })

    df_project = pd.DataFrame({
        'project': data['project'],
        'story_points': data['story_points_project']
    })

    # Create bar chart for Sprint vs Story Points
    sprint_storypoints_fig = px.bar(df_sprint, x='sprint', y='story_points', title='Sprint vs Story Points')

    # Create bar chart for Assignee vs Story Points
    assignee_storypoints_fig = px.bar(df_assignee, x='assignee', y='story_points', title='Assignee vs Story Points')

    # Create pie chart for Project vs Sum of Story Points
    project_storypoints_pie_fig = px.pie(df_project, names='project', values='story_points', title='Project vs Sum of Story Points')

    return sprint_storypoints_fig, assignee_storypoints_fig, project_storypoints_pie_fig

if __name__ == '__main__':
    app.run_server(debug=True)

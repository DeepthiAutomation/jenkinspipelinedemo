import dash_core_components as dcc
import dash_html_components as html
import dash_table
from dash.dependencies import Input, Output, State
import plotly.express as px
import requests
import sqlite3
import pandas as pd
import dash_bootstrap_components as dbc
from app import app

# Authentication for JIRA (replace with your credentials)
auth = ('username', 'password')

# Fetch projects from the database
def get_projects():
    conn = sqlite3.connect('jira_dashboard.db')
    df = pd.read_sql_query('SELECT url, project_name FROM projects', conn)
    conn.close()
    return df

# Fetch custom fields from the database
def get_custom_fields():
    conn = sqlite3.connect('jira_dashboard.db')
    df = pd.read_sql_query('SELECT url, field_id, field_name FROM customfields', conn)
    conn.close()
    return df

projects_df = get_projects()
custom_fields_df = get_custom_fields()

# Define table styles
table_style = {
    'header': {
        'backgroundColor': 'navy',
        'fontWeight': 'bold',
        'color': 'white',
        'textAlign': 'center'
    },
    'cell': {
        'padding': '10px',
        'textAlign': 'left'
    },
    'evenRow': {
        'backgroundColor': 'rgb(248, 248, 248)'
    },
    'oddRow': {
        'backgroundColor': 'white'
    }
}

layout = html.Div([
    html.H1("Get Stories", style={'textAlign': 'center', 'fontFamily': 'Arial, sans-serif'}),
    
    html.Div([
        html.Label("Select Projects:"),
        dcc.Dropdown(
            id='project-dropdown',
            options=[{'label': row['project_name'], 'value': row['project_name']} for _, row in projects_df.iterrows()],
            multi=True
        ),
        
        html.Label("Select Assignee:"),
        dcc.Dropdown(
            id='assignee-dropdown',
            multi=True
        ),
        
        html.Label("Enter Filter (Label, Epic, Assignee, Reporter, Sprint):"),
        dcc.Input(id='filter-input', type='text', value=''),
        
        dcc.Checklist(
            id='open-sprints-checkbox',
            options=[{'label': 'Open Sprints Only', 'value': 'openSprints'}],
            value=['openSprints'],
            style={'marginTop': '10px'}
        ),
        
        html.Button('Get Stories', id='get-stories-button', n_clicks=0, className='btn btn-success', style={'marginTop': '10px', 'marginRight': '10px'}),
        dcc.Link('Back to Home', href='/', className='btn btn-secondary', style={'marginTop': '10px'}),
    ], style={'padding': '20px'}),
    
    html.Div([
        dcc.Graph(id='status-storypoints-pie', style={'display': 'none'}, className='four columns'),
        dcc.Graph(id='epic-storypoints-pie', style={'display': 'none'}, className='four columns'),
        dcc.Graph(id='missing-fields-pie', style={'display': 'none'}, className='four columns'),
    ], className='row'),

    html.Div([
        dash_table.DataTable(
            id='stories-table',
            columns=[
                {'name': 'Project', 'id': 'project'},
                {'name': 'Story Key', 'id': 'key', 'presentation': 'markdown'},
                {'name': 'Summary', 'id': 'summary'},
                {'name': 'Assignee', 'id': 'assignee'},
                {'name': 'Status', 'id': 'status'},
                {'name': 'Story Points', 'id': 'story_points'},
                {'name': 'Epic Link', 'id': 'epic_link'}
            ],
            data=[],
            style_header=table_style['header'],
            style_cell=table_style['cell'],
            style_data_conditional=[
                {'if': {'row_index': 'odd'}, 'backgroundColor': table_style['oddRow']['backgroundColor']},
                {'if': {'row_index': 'even'}, 'backgroundColor': table_style['evenRow']['backgroundColor']}
            ],
            filter_action='native',
            sort_action='native',
            page_action='native',
            page_size=10
        ),
    ]),

    html.Div([
        dcc.Graph(id='assignee-storypoints-chart', style={'display': 'none'}, className='six columns'),
        dcc.Graph(id='status-count-chart', style={'display': 'none'}, className='six columns'),
    ], className='row'),
    
    html.Div([
        dcc.Graph(id='assignee-status-chart', style={'display': 'none'}, className='six columns'),
    ], className='row')
])

@app.callback(
    [Output('assignee-dropdown', 'options', allow_duplicate=True),
     Output('stories-table', 'data', allow_duplicate=True), 
     Output('error-message', 'children', allow_duplicate=True),
     Output('assignee-storypoints-chart', 'figure', allow_duplicate=True),
     Output('status-count-chart', 'figure', allow_duplicate=True),
     Output('assignee-status-chart', 'figure', allow_duplicate=True),
     Output('status-storypoints-pie', 'figure', allow_duplicate=True),
     Output('epic-storypoints-pie', 'figure', allow_duplicate=True),
     Output('missing-fields-pie', 'figure', allow_duplicate=True),
     Output('assignee-storypoints-chart', 'style', allow_duplicate=True),
     Output('status-count-chart', 'style', allow_duplicate=True),
     Output('assignee-status-chart', 'style', allow_duplicate=True),
     Output('status-storypoints-pie', 'style', allow_duplicate=True),
     Output('epic-storypoints-pie', 'style', allow_duplicate=True),
     Output('missing-fields-pie', 'style', allow_duplicate=True)],
    [Input('get-stories-button', 'n_clicks')],
    [State('project-dropdown', 'value'), State('assignee-dropdown', 'value'), State('filter-input', 'value'), State('open-sprints-checkbox', 'value')]
)
def get_stories(n_clicks, selected_projects, selected_assignees, filter_input, open_sprints):
    if n_clicks == 0:
        return [], [], '', {}, {}, {}, {}, {}, {}, {'display': 'none'}, {'display': 'none'}, {'display': 'none'}, {'display': 'none'}, {'display': 'none'}, {'display': 'none'}

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
    html.H1("Get Backlogs", style={'textAlign': 'center', 'fontFamily': 'Arial, sans-serif'}),
    
    html.Div([
        html.Label("Select Projects:"),
        dcc.Dropdown(
            id='backlog-project-dropdown',
            options=[{'label': row['project_name'], 'value': row['project_name']} for _, row in projects_df.iterrows()],
            multi=True
        ),
        
        html.Label("Select Assignee:"),
        dcc.Dropdown(
            id='backlog-assignee-dropdown',
            multi=True
        ),
        
        html.Label("Enter Filter (Label, Epic, Assignee, Reporter, Sprint):"),
        dcc.Input(id='backlog-filter-input', type='text', value=''),
        
        html.Button('Get Backlogs', id='get-backlogs-button', n_clicks=0, className='btn btn-success', style={'marginTop': '10px'}),
        dcc.Link('Back to Home', href='/', className='btn btn-secondary', style={'marginTop': '10px', 'marginLeft': '10px'}),
    ], style={'padding': '20px'}),
    
    dash_table.DataTable(
        id='backlogs-table',
        columns=[
            {'name': 'Project', 'id': 'project'},
            {'name': 'Story Key', 'id': 'key', 'presentation': 'markdown'},
            {'name': 'Summary', 'id': 'summary'},
            {'name': 'Assignee', 'id': 'assignee'},
            {'name': 'Reporter', 'id': 'reporter'},
            {'name': 'Status', 'id': 'status'},
            {'name': 'Created', 'id': 'created'},
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
    
    html.Div(id='backlog-error-message', style={'color': 'red', 'padding': '10px'}),
    
    html.Div([
        dcc.Graph(id='reporter-count-chart', style={'display': 'none'}),
        dcc.Graph(id='epic-count-chart', style={'display': 'none'}),
        dcc.Graph(id='created-quarter-count-chart', style={'display': 'none'}),
        dcc.Graph(id='missing-epicname-count-chart', style={'display': 'none'})
    ])
])

@app.callback(
    [Output('backlog-assignee-dropdown', 'options', allow_duplicate=True),
     Output('backlogs-table', 'data', allow_duplicate=True), 
     Output('backlog-error-message', 'children', allow_duplicate=True),
     Output('reporter-count-chart', 'figure', allow_duplicate=True),
     Output('epic-count-chart', 'figure', allow_duplicate=True),
     Output('created-quarter-count-chart', 'figure', allow_duplicate=True),
     Output('missing-epicname-count-chart', 'figure', allow_duplicate=True),
     Output('reporter-count-chart', 'style', allow_duplicate=True),
     Output('epic-count-chart', 'style', allow_duplicate=True),
     Output('created-quarter-count-chart', 'style', allow_duplicate=True),
     Output('missing-epicname-count-chart', 'style', allow_duplicate=True)],
    [Input('get-backlogs-button', 'n_clicks')],
    [State('backlog-project-dropdown', 'value'), State('backlog-assignee-dropdown', 'value'), State('backlog-filter-input', 'value')]
)
def get_backlogs(n_clicks, selected_projects, selected_assignees, filter_input):
    if n_clicks == 0:
        return [], [], '', {}, {}, {}, {}, {'display': 'none'}, {'display': 'none'}, {'display': 'none'}, {'display': 'none'}
    
    filter_input = filter_input.strip()
    filter_type, *filter_values = filter_input.split(':', 1)
    filter_values = filter_values[0].strip().split(',') if filter_values else []
    
    backlogs = []
    error_message = ''
    
    if selected_projects:
        # Create a dictionary to map projects to their URLs
        project_to_url = {row['project_name']: row['url'] for _, row in projects_df.iterrows()}
        
        for project in selected_projects:
            jira_url = project_to_url.get(project)
            if not jira_url:
                continue
            
            # Get the custom fields for the given URL
            custom_fields = custom_fields_df[custom_fields_df['url'] == jira_url]
            epic_link_field = custom_fields[custom_fields['field_name'] == 'Epic Link']['field_id'].values[0]
            
            # Construct JQL query
            jql_parts = [f'project = "{project}" AND issuetype = Story AND status not in (Done, Closed)']
            
            if selected_assignees:
                assignee_list = ', '.join([f'"{assignee}"' for assignee in selected_assignees])
                jql_parts.append(f'assignee IN ({assignee_list})')
            
            if filter_values:
                if filter_type.lower() == 'label':
                    filter_list = ', '.join([f'"{value}"' for value in filter_values])
                    jql_parts.append(f'labels IN ({filter_list})')
                elif filter_type.lower() == 'epic':
                    filter_list = ', '.join([f'"{value}"' for value in filter_values])
                    jql_parts.append(f'epicLink IN ({filter_list})')
                elif filter_type.lower() == 'reporter':
                    filter_list = ', '.join([f'"{value}"' for value in filter_values])
                    jql_parts.append(f'reporter IN ({filter_list})')
                elif filter_type.lower() == 'sprint':
                    filter_list = ', '.join([f'"{value}"' for value in filter_values])
                    jql_parts.append(f'sprint IN ({filter_list})')
            
            jql = ' AND '.join(jql_parts)
            
            response = requests.get(f'{jira_url}/rest/api/2/search?jql={jql}&fields=key,summary,assignee,reporter,status,created,{epic_link_field}', auth=auth)
            
            if response.status_code != 200:
                error_message = f"Error fetching data from {jira_url}: {response.content}"
                continue
            
            issues = response.json().get('issues', [])
            for issue in issues:
                fields = issue['fields']
                backlog = {
                    'project': project,
                    'key': f"[{issue['key']}]({jira_url}/browse/{issue['key']})",
                    'summary': fields.get('summary'),
                    'assignee': fields.get('assignee', {}).get('displayName'),
                    'reporter': fields.get('reporter', {}).get('displayName'),
                    'status': fields.get('status', {}).get('name'),
                    'created': fields.get('created'),
                    'epic_link': fields.get(epic_link_field)
                }
                backlogs.append(backlog)
    
    if not backlogs:
        return [], [], error_message, {}, {}, {}, {}, {'display': 'none'}, {'display': 'none'}, {'display': 'none'}, {'display': 'none'}
    
    df = pd.DataFrame(backlogs)
    
    reporter_count_fig = px.bar(df, x='reporter', title='Reporter vs Count')
    epic_count_fig = px.bar(df, x='epic_link', title='Epic vs Count')
    df['created_quarter'] = pd.to_datetime(df['created']).dt.to_period('Q')
    created_quarter_count_fig = px.bar(df, x='created_quarter', title='Created Quarter vs Count')
    missing_epicname_count_fig = px.bar(df[df['epic_link'].isnull()], x='project', title='Missing Epic Name vs Count')
    
    assignees = [{'label': assignee, 'value': assignee} for assignee in df['assignee'].unique()]
    
    return (assignees, backlogs, '', reporter_count_fig, epic_count_fig, created_quarter_count_fig, missing_epicname_count_fig,
            {'display': 'block'}, {'display': 'block'}, {'display': 'block'}, {'display': 'block'})

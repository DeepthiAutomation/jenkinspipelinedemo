import dash
import dash_core_components as dcc
import dash_html_components as html
import dash_table
from dash.dependencies import Input, Output, State
import plotly.express as px
import requests
import sqlite3
import pandas as pd
import dash_bootstrap_components as dbc

# Initialize the Dash app
app = dash.Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])
server = app.server  # Expose the server variable for gunicorn

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

app.layout = html.Div([
    html.H1("JIRA Dashboard", style={'textAlign': 'center', 'fontFamily': 'Arial, sans-serif'}),
    
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
        html.Button('Get Backlogs', id='get-backlogs-button', n_clicks=0, className='btn btn-success', style={'marginTop': '10px'}),
    ], style={'padding': '20px'}),
    
    dash_table.DataTable(
        id='stories-table',
        columns=[
            {'name': 'Project', 'id': 'project'},
            {'name': 'Story Key', 'id': 'key', 'presentation': 'markdown'},
            {'name': 'Summary', 'id': 'summary'},
            {'name': 'Assignee', 'id': 'assignee'},
            {'name': 'Status', 'id': 'status'},
            {'name': 'Sprint', 'id': 'sprint'},
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
    
    html.Div(id='error-message', style={'color': 'red', 'padding': '10px'}),
    
    html.Div([
        dcc.Graph(id='assignee-storypoints-chart', style={'display': 'none'}),
        dcc.Graph(id='status-count-chart', style={'display': 'none'}),
        dcc.Graph(id='assignee-status-chart', style={'display': 'none'})
    ]),
    
    html.Div([
        dcc.Graph(id='reporter-count-chart', style={'display': 'none'}),
        dcc.Graph(id='epic-count-chart', style={'display': 'none'}),
        dcc.Graph(id='created-quarter-count-chart', style={'display': 'none'}),
        dcc.Graph(id='missing-epicname-count-chart', style={'display': 'none'})
    ]),
    
    html.Div([
        dcc.Graph(id='status-storypoints-pie', style={'display': 'none'}),
        dcc.Graph(id='epic-storypoints-pie', style={'display': 'none'}),
        dcc.Graph(id='missing-fields-pie', style={'display': 'none'})
    ])
])

@app.callback(
    [Output('assignee-dropdown', 'options'),
     Output('stories-table', 'data'), 
     Output('error-message', 'children'),
     Output('assignee-storypoints-chart', 'figure'),
     Output('assignee-storypoints-chart', 'style'),
     Output('status-count-chart', 'figure'),
     Output('status-count-chart', 'style'),
     Output('assignee-status-chart', 'figure'),
     Output('assignee-status-chart', 'style'),
     Output('status-storypoints-pie', 'figure'),
     Output('status-storypoints-pie', 'style'),
     Output('epic-storypoints-pie', 'figure'),
     Output('epic-storypoints-pie', 'style'),
     Output('missing-fields-pie', 'figure'),
     Output('missing-fields-pie', 'style')],
    [Input('get-stories-button', 'n_clicks')],
    [State('project-dropdown', 'value'), State('assignee-dropdown', 'value'), State('filter-input', 'value'), State('open-sprints-checkbox', 'value')]
)
def get_stories(n_clicks, selected_projects, selected_assignees, filter_input, open_sprints):
    if n_clicks == 0:
        return [], [], '', {}, {'display': 'none'}, {}, {'display': 'none'}, {}, {'display': 'none'}, {}, {'display': 'none'}, {}, {'display': 'none'}, {}, {'display': 'none'}
    
    filter_input = filter_input.strip()
    filter_type, *filter_values = filter_input.split(':', 1)
    filter_values = filter_values[0].strip().split(',') if filter_values else []
    
    stories = []
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
            sprint_field = custom_fields[custom_fields['field_name'] == 'Sprint']['field_id'].values[0]
            story_points_field = custom_fields[custom_fields['field_name'] == 'Story Points']['field_id'].values[0]
            epic_link_field = custom_fields[custom_fields['field_name'] == 'Epic Link']['field_id'].values[0]
            
            # Construct JQL query
            jql_parts = [f'project = "{project}"']
            
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
            
            if open_sprints:
                jql_parts.append('sprint in openSprints()')
            
            jql = ' AND '.join(jql_parts)
            
            response = requests.get(f'{jira_url}/rest/api/2/search?jql={jql}&fields=key,summary,assignee,status,{sprint_field},{story_points_field},{epic_link_field}', auth=auth)
            
            if response.status_code != 200:
                error_message = f"Error fetching data from {jira_url}: {response.content}"
                continue
            
            issues = response.json().get('issues', [])
            for issue in issues:
                fields = issue['fields']
                story = {
                    'project': project,
                    'key': f"[{issue['key']}]({jira_url}/browse/{issue['key']})",
                    'summary': fields.get('summary'),
                    'assignee': fields.get('assignee', {}).get('displayName'),
                    'status': fields.get('status', {}).get('name'),
                    'sprint': fields.get(sprint_field, {}).get('name'),
                    'story_points': fields.get(story_points_field),
                    'epic_link': fields.get(epic_link_field)
                }
                stories.append(story)
    
    if not stories:
        return [], [], error_message, {}, {'display': 'none'}, {}, {'display': 'none'}, {}, {'display': 'none'}, {}, {'display': 'none'}, {}, {'display': 'none'}, {}, {'display': 'none'}
    
    df = pd.DataFrame(stories)
    
    assignee_storypoints_fig = px.bar(df, x='assignee', y='story_points', title='Assignee vs Story Points')
    status_count_fig = px.bar(df, x='status', title='Status vs Count')
    assignee_status_fig = px.bar(df, x='assignee', color='status', barmode='group', title='Assignee vs Status Count')
    
    # Pie charts
    status_storypoints_pie = px.pie(df, names='status', values='story_points', title='Story Points by Status')
    epic_storypoints_pie = px.pie(df, names='epic_link', values='story_points', title='Story Points by Epic')
    
    missing_fields_count = {
        'No Epic Link': len(df[df['epic_link'].isnull()]),
        'No Story Points': len(df[df['story_points'].isnull()]),
        'No Acceptance Criteria': len(df[df['summary'].str.contains('Acceptance Criteria') == False]),
        'Unassigned': len(df[df['assignee'].isnull()])
    }
    missing_fields_pie = px.pie(names=list(missing_fields_count.keys()), values=list(missing_fields_count.values()), title='Missing Fields Count')
    
    assignees = [{'label': assignee, 'value': assignee} for assignee in df['assignee'].unique()]
    
    return (assignees, stories, '', assignee_storypoints_fig, {'display': 'block'}, 
            status_count_fig, {'display': 'block'}, assignee_status_fig, {'display': 'block'},
            status_storypoints_pie, {'display': 'block'}, epic_storypoints_pie, {'display': 'block'}, missing_fields_pie, {'display': 'block'})

@app.callback(
    [Output('assignee-dropdown', 'options'),
     Output('stories-table', 'data'), 
     Output('error-message', 'children'),
     Output('reporter-count-chart', 'figure'),
     Output('reporter-count-chart', 'style'),
     Output('epic-count-chart', 'figure'),
     Output('epic-count-chart', 'style'),
     Output('created-quarter-count-chart', 'figure'),
     Output('created-quarter-count-chart', 'style'),
     Output('missing-epicname-count-chart', 'figure'),
     Output('missing-epicname-count-chart', 'style')],
    [Input('get-backlogs-button', 'n_clicks')],
    [State('project-dropdown', 'value'), State('assignee-dropdown', 'value'), State('filter-input', 'value')]
)
def get_backlogs(n_clicks, selected_projects, selected_assignees, filter_input):
    if n_clicks == 0:
        return [], [], '', {}, {'display': 'none'}, {}, {'display': 'none'}, {}, {'display': 'none'}, {}, {'display': 'none'}
    
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
        return [], [], error_message, {}, {'display': 'none'}, {}, {'display': 'none'}, {}, {'display': 'none'}, {}, {'display': 'none'}
    
    df = pd.DataFrame(backlogs)
    
    reporter_count_fig = px.bar(df, x='reporter', title='Reporter vs Count')
    epic_count_fig = px.bar(df, x='epic_link', title='Epic vs Count')
    df['created_quarter'] = pd.to_datetime(df['created']).dt.to_period('Q')
    created_quarter_count_fig = px.bar(df, x='created_quarter', title='Created Quarter vs Count')
    missing_epicname_count_fig = px.bar(df[df['epic_link'].isnull()], x='project', title='Missing Epic Name vs Count')
    
    assignees = [{'label': assignee, 'value': assignee} for assignee in df['assignee'].unique()]
    
    return (assignees, backlogs, '', reporter_count_fig, {'display': 'block'}, 
            epic_count_fig, {'display': 'block'}, created_quarter_count_fig, {'display': 'block'}, missing_epicname_count_fig, {'display': 'block'})

if __name__ == '__main__':
    app.run_server(debug=True)

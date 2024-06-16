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
        
        html.Label("Enter Labels (comma separated):"),
        dcc.Input(id='label-input', type='text', value=''),
        
        html.Button('Get Stories', id='get-stories-button', n_clicks=0, className='btn btn-success', style={'marginTop': '10px'}),
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
    ])
])

@app.callback(
    [Output('stories-table', 'data'), 
     Output('error-message', 'children'),
     Output('assignee-storypoints-chart', 'figure'),
     Output('assignee-storypoints-chart', 'style'),
     Output('status-count-chart', 'figure'),
     Output('status-count-chart', 'style'),
     Output('assignee-status-chart', 'figure'),
     Output('assignee-status-chart', 'style')],
    [Input('get-stories-button', 'n_clicks')],
    [State('project-dropdown', 'value'), State('label-input', 'value')]
)
def get_stories(n_clicks, selected_projects, labels_input):
    if n_clicks == 0:
        return [], '', {}, {'display': 'none'}, {}, {'display': 'none'}, {}, {'display': 'none'}
    
    # Parse the labels input
    labels = [label.strip() for label in labels_input.split(',') if label.strip()]
    
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
            
            if labels:
                label_list = ', '.join([f'"{label}"' for label in labels])
                jql_parts.append(f'labels IN ({label_list})')
            
            jql_parts.append('status = "Open" AND sprint in openSprints()')
            
            jql = ' AND '.join(jql_parts)
            
            # Fetch stories from JIRA
            search_url = f'{jira_url}/rest/api/2/search'
            response = requests.get(search_url, params={'jql': jql}, auth=auth)
            if response.status_code == 200:
                issues = response.json().get('issues', [])
                for issue in issues:
                    fields = issue.get('fields', {})
                    story = {
                        'project': project,
                        'key': f"[{issue['key']}]({jira_url}/browse/{issue['key']})",
                        'summary': fields.get('summary', ''),
                        'assignee': fields.get('assignee', {}).get('displayName', 'Unassigned'),
                        'status': fields.get('status', {}).get('name', ''),
                        'sprint': ', '.join(sprint.get('name', '') for sprint in fields.get(sprint_field, [])),
                        'story_points': fields.get(story_points_field, 0),
                        'epic_link': fields.get(epic_link_field, '')
                    }
                    stories.append(story)
            else:
                error_message += f"Error fetching data from {jira_url} for project {project}: {response.status_code} - {response.text}\n"
    else:
        # If no projects are selected, query all projects from all URLs
        urls = projects_df['url'].unique()
        
        for jira_url in urls:
            # Get the custom fields for the given URL
            custom_fields = custom_fields_df[custom_fields_df['url'] == jira_url]
            sprint_field = custom_fields[custom_fields['field_name'] == 'Sprint']['field_id'].values[0]
            story_points_field = custom_fields[custom_fields['field_name'] == 'Story Points']['field_id'].values[0]
            epic_link_field = custom_fields[custom_fields['field_name'] == 'Epic Link']['field_id'].values[0]
            
            # Construct JQL query
            jql_parts = []
            
            if labels:
                label_list = ', '.join([f'"{label}"' for label in labels])
                jql_parts.append(f'labels IN ({label_list})')
            
            jql_parts.append('status = "Open" AND sprint in openSprints()')
            
            jql = ' AND '.join(jql_parts)
            
            # Fetch stories from JIRA
            search_url = f'{jira_url}/rest/api/2/search'
            response = requests.get(search_url, params={'jql': jql}, auth=auth)
            if response.status_code == 200:
                issues = response.json().get('issues', [])
                for issue in issues:
                    fields = issue.get('fields', {})
                    project_name = fields.get('project', {}).get('name', 'Unknown')

                    story = {
                        'project': project_name,
                        'key': f"[{issue['key']}]({jira_url}/browse/{issue['key']})",
                        'summary': fields.get('summary', ''),
                        'assignee': fields.get('assignee', {}).get('displayName', 'Unassigned'),
                        'status': fields.get('status', {}).get('name', ''),
                        'sprint': ', '.join(sprint.get('name', '') for sprint in fields.get(sprint_field, [])),
                        'story_points': fields.get(story_points_field, 0),
                        'epic_link': fields.get(epic_link_field, '')
                    }
                    stories.append(story)
            else:
                error_message += f"Error fetching data from {jira_url}: {response.status_code} - {response.text}\n"
    
    # Create dataframes for plotting
    df_stories = pd.DataFrame(stories)

    # Create the figures for the bar charts
    if not df_stories.empty:
        fig_assignee_storypoints = px.bar(
            df_stories.groupby('assignee').sum().reset_index(), 
            x='assignee', 
            y='story_points', 
            title='Assignee vs. Story Points (Aggregated)'
        )
        
        fig_status_count = px.bar(
            df_stories['status'].value_counts().reset_index(), 
            x='index', 
            y='status', 
            title='Status vs. Count'
        )
        
        fig_assignee_status = px.bar(
            df_stories.groupby(['assignee', 'status']).size().reset_index(name='count'), 
            x='assignee', 
            y='count', 
            color='status', 
            title='Assignee vs. Status Count'
        )
        
        charts_style = {'display': 'block'}
    else:
        fig_assignee_storypoints = {}
        fig_status_count = {}
        fig_assignee_status = {}
        charts_style = {'display': 'none'}

    return stories, error_message, fig_assignee_storypoints, charts_style, fig_status_count, charts_style, fig_assignee_status, charts_style

if __name__ == '__main__':
    app.run_server(debug=True)

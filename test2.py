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

# Authentication for JIRA (replace with your credentials)
auth = ('username', 'password')

# Fetch projects from the database
def get_projects():
    conn = sqlite3.connect('jira_dashboard.db')
    df = pd.read_sql_query('SELECT url, project_name FROM projects', conn)
    conn.close()
    return df

projects_df = get_projects()

app.layout = html.Div([
    html.H1("JIRA Dashboard"),
    
    html.Label("Select Projects:"),
    dcc.Dropdown(
        id='project-dropdown',
        options=[{'label': row['project_name'], 'value': row['project_name']} for _, row in projects_df.iterrows()],
        multi=True
    ),
    
    html.Label("Enter Labels (comma separated):"),
    dcc.Input(id='label-input', type='text', value=''),
    
    html.Button('Get Stories', id='get-stories-button', n_clicks=0),
    
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
        data=[]
    ),
    
    html.Div(id='error-message', style={'color': 'red'})
])

@app.callback(
    [Output('stories-table', 'data'), Output('error-message', 'children')],
    [Input('get-stories-button', 'n_clicks')],
    [State('project-dropdown', 'value'), State('label-input', 'value')]
)
def get_stories(n_clicks, selected_projects, labels_input):
    if n_clicks == 0:
        return [], ''
    
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
                    fields = issue['fields']
                    story = {
                        'project': project,
                        'key': f"[{issue['key']}]({jira_url}/browse/{issue['key']})",
                        'summary': fields.get('summary', ''),
                        'assignee': fields.get('assignee', {}).get('displayName', 'Unassigned'),
                        'status': fields.get('status', {}).get('name', ''),
                        'sprint': ', '.join(sprint.get('name', '') for sprint in fields.get('customfield_10007', [])),
                        'story_points': fields.get('customfield_10004', ''),
                        'epic_link': fields.get('customfield_10008', '')
                    }
                    stories.append(story)
            else:
                error_message += f"Error fetching data from {jira_url} for project {project}: {response.status_code} - {response.text}\n"
    else:
        # If no projects are selected, query all projects from all URLs
        urls = projects_df['url'].unique()
        
        for jira_url in urls:
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
                    fields = issue['fields']
                    story = {
                        'project': fields.get('project', {}).get('name', 'Unknown'),
                        'key': f"[{issue['key']}]({jira_url}/browse/{issue['key']})",
                        'summary': fields.get('summary', ''),
                        'assignee': fields.get('assignee', {}).get('displayName', 'Unassigned'),
                        'status': fields.get('status', {}).get('name', ''),
                        'sprint': ', '.join(sprint.get('name', '') for sprint in fields.get('customfield_10007', [])),
                        'story_points': fields.get('customfield_10004', ''),
                        'epic_link': fields.get('customfield_10008', '')
                    }
                    stories.append(story)
            else:
                error_message += f"Error fetching data from {jira_url}: {response.status_code} - {response.text}\n"
    
    return stories, error_message

if __name__ == '__main__':
    app.run_server(debug=True)

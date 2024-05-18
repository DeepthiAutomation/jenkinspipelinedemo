import dash
from dash import html, dcc
from dash.dependencies import Input, Output, State
import requests
import pandas as pd
import base64
import os
import schedule
import time
import shutil

# Jira configuration for three domains
JIRA_DOMAINS = [
    'your-domain1.atlassian.net',
    'your-domain2.atlassian.net',
    'your-domain3.atlassian.net'
]
JIRA_EMAILS = [
    'your-email1@example.com',
    'your-email2@example.com',
    'your-email3@example.com'
]

# Define your label value
LABEL_VALUE = "your_label_value"

# Define custom field IDs for each domain
CUSTOM_FIELD_IDS = {
    'your-domain1.atlassian.net': {
        'sprint': 'customfield_10007',
        'story_points': 'customfield_10002',
        'epic_link': 'customfield_10008'
    },
    'your-domain2.atlassian.net': {
        'sprint': 'customfield_20007',
        'story_points': 'customfield_20002',
        'epic_link': 'customfield_20008'
    },
    'your-domain3.atlassian.net': {
        'sprint': 'customfield_30007',
        'story_points': 'customfield_30002',
        'epic_link': 'customfield_30008'
    }
}

JQL_QUERY = f'project = YOUR_PROJECT AND labels = "{LABEL_VALUE}" AND Sprint in openSprints()'

# Helper function to get Jira data
def get_jira_data(domain, email):
    api_token = os.getenv(f'JIRA_API_TOKEN_{domain.replace(".", "_").upper()}')
    if not api_token:
        raise ValueError(f"API token for {domain} not found in environment variables.")
    
    url = f"https://{domain}/rest/api/3/search"
    auth = base64.b64encode(f"{email}:{api_token}".encode()).decode()
    headers = {
        "Authorization": f"Basic {auth}",
        "Content-Type": "application/json"
    }
    params = {
        "jql": JQL_QUERY,
        "fields": f"key,summary,assignee,status,{CUSTOM_FIELD_IDS[domain]['sprint']},{CUSTOM_FIELD_IDS[domain]['story_points']},{CUSTOM_FIELD_IDS[domain]['epic_link']}",
        "maxResults": 100
    }
    response = requests.get(url, headers=headers, params=params)
    if response.status_code == 200:
        return response.json()
    else:
        return None

# Function to update CSV file
def update_csv():
    temp_filename = 'temp_jira_issues.csv'
    all_issues = []
    for domain, email in zip(JIRA_DOMAINS, JIRA_EMAILS):
        data = get_jira_data(domain, email)
        if data:
            all_issues.extend(data.get('issues', []))

    if all_issues:
        df = pd.DataFrame([{
            'Key': issue['key'],
            'Summary': issue['fields']['summary'],
            'Assignee': issue['fields']['assignee']['displayName'] if issue['fields']['assignee'] else 'Unassigned',
            'Status': issue['fields']['status']['name'],
            'Sprint': issue['fields'][CUSTOM_FIELD_IDS[domain]['sprint']][0]['name'] if issue['fields'].get(CUSTOM_FIELD_IDS[domain]['sprint']) else 'None',
            'Story Points': issue['fields'].get(CUSTOM_FIELD_IDS[domain]['story_points'], 'None'),
            'Epic Link': issue['fields'].get(CUSTOM_FIELD_IDS[domain]['epic_link'], 'None')
        } for issue in all_issues])
        
        # Write to temporary CSV file
        df.to_csv(temp_filename, index=False)

        # Replace original CSV file with temporary one
        shutil.move(temp_filename, 'jira_issues.csv')

# Update CSV file every 5 minutes
schedule.every(5).minutes.do(update_csv)

# Initialize the Dash app
app = dash.Dash(__name__)

# Define the layout of the app
app.layout = html.Div(
    style={'textAlign': 'center', 'padding': '50px'},
    children=[
        html.H1('Jira Open Sprints with Label'),
        html.Div([
            html.Label('Select Assignee:'),
            dcc.Dropdown(id='assignee-dropdown', placeholder='Select an assignee'),
        ], style={'width': '50%', 'margin': 'auto'}),
        html.Button('Fetch Data', id='fetch-button'),
        dcc.Interval(id='interval-component', interval=60000, n_intervals=0),  # Refresh every 60 seconds
        html.Div(id='jira-data-container', style={'margin': '20px'})
    ]
)

# Define the callback to update the assignee dropdown
@app.callback(
    Output('assignee-dropdown', 'options'),
    Input('interval-component', 'n_intervals')
)
def update_assignee_dropdown(n_intervals):
    all_issues = []
    for domain, email in zip(JIRA_DOMAINS, JIRA_EMAILS):
        data = get_jira_data(domain, email)
        if data:
            all_issues.extend(data.get('issues', []))

    assignees = [{'label': issue['fields']['assignee']['displayName'], 'value': issue['fields']['assignee']['accountId']}
                 for issue in all_issues if issue['fields']['assignee']]
    # Remove duplicates
    unique_assignees = {v['value']: v for v in assignees}.values()
    return list(unique_assignees)

# Define the callback to update the data
@app.callback(
    Output('jira-data-container', 'children'),
    [Input('fetch-button', 'n

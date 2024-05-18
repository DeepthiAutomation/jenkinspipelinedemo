import dash
from dash import html, dcc
from dash.dependencies import Input, Output, State
import requests
import pandas as pd
import base64
import os

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

JQL_QUERY = 'project = YOUR_PROJECT AND labels = your_label AND Sprint in openSprints()'

# Replace these with your Jira custom field IDs
CUSTOM_FIELD_SPRINT = 'customfield_10007'
CUSTOM_FIELD_STORY_POINTS = 'customfield_10002'
CUSTOM_FIELD_EPIC_LINK = 'customfield_10008'

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
        "fields": f"key,summary,assignee,status,{CUSTOM_FIELD_SPRINT},{CUSTOM_FIELD_STORY_POINTS},{CUSTOM_FIELD_EPIC_LINK}",
        "maxResults": 100
    }
    response = requests.get(url, headers=headers, params=params)
    if response.status_code == 200:
        return response.json()
    else:
        return None

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
    [Input('fetch-button', 'n_clicks'),
     Input('interval-component', 'n_intervals')],
    [State('assignee-dropdown', 'value')]
)
def update_data(n_clicks, n_intervals, selected_assignee):
    all_issues = []
    for domain, email in zip(JIRA_DOMAINS, JIRA_EMAILS):
        if selected_assignee:
            jql = JQL_QUERY + f' AND assignee="{selected_assignee}"'
        else:
            jql = JQL_QUERY

        data = get_jira_data(domain, email)
        if data:
            all_issues.extend(data.get('issues', []))

    if not all_issues:
        return html.Div("No issues found.")

    # Create a DataFrame for better visualization
    df = pd.DataFrame([{
        'Key': issue['key'],
        'Summary': issue['fields']['summary'],
        'Assignee': issue['fields']['assignee']['displayName'] if issue['fields']['assignee'] else 'Unassigned',
        'Status': issue['fields']['status']['name'],
        'Sprint': issue['fields'][CUSTOM_FIELD_SPRINT][0]['name'] if issue['fields'].get(CUSTOM_FIELD_SPRINT) else 'None',
        'Story Points': issue['fields'].get(CUSTOM_FIELD_STORY_POINTS, 'None'),
        'Epic Link': issue['fields'].get(CUSTOM_FIELD_EPIC_LINK, 'None')
    } for issue in all_issues])

    return html.Div([
        html.H3(f"Found {len(all_issues)} issues:"),
        html.Table([
            html.Thead(html.Tr([html.Th(col) for col in df.columns])),
            html.Tbody([
                html.Tr([
                    html.Td(df.iloc[i][col]) for col in df.columns
                ]) for i in range(len(df))
            ])
        ])
    ])

# Run the app
if __name__ == '__main__':
    app.run_server(debug=True)

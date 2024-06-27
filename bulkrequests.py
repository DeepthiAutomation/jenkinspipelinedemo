import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output, State
import requests
import pandas as pd
import dash_bootstrap_components as dbc

# Initialize the Dash app
app = dash.Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP], suppress_callback_exceptions=True)

# Authentication for JIRA (replace with your credentials)
auth = ('username', 'password')

# Fetch projects from the database
def get_projects():
    conn = sqlite3.connect('jira_dashboard.db')
    df = pd.read_sql_query('SELECT url, project_name FROM projects', conn)
    conn.close()
    return df

projects_df = get_projects()

# Home Page Layout
home_layout = html.Div([
    html.H1("Welcome to JIRA Dashboard", style={'textAlign': 'center', 'fontFamily': 'Arial, sans-serif'}),
    html.Div([
        dcc.Link('Get Stories', href='/stories', className='btn btn-success', style={'marginRight': '10px'}),
        dcc.Link('Get Backlogs', href='/backlogs', className='btn btn-success', style={'marginRight': '10px'}),
        dcc.Link('Bulk Create Stories', href='/bulk-create', className='btn btn-success')
    ], style={'textAlign': 'center', 'padding': '20px'})
])

# Bulk Create Stories Page Layout
bulk_create_layout = html.Div([
    html.H1("Bulk Create Stories", style={'textAlign': 'center', 'fontFamily': 'Arial, sans-serif'}),
    html.Div([
        html.Label("Select Project:"),
        dcc.Dropdown(
            id='project-dropdown',
            options=[{'label': row['project_name'], 'value': row['project_name']} for _, row in projects_df.iterrows()]
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
    else:
        return home_layout

# Callback to handle story creation
@app.callback(
    Output('creation-result', 'children'),
    [Input('create-stories-button', 'n_clicks')],
    [State('project-dropdown', 'value'), State('epic-input', 'value'), State('sprint-input', 'value'),
     State('label-input', 'value'), State('summaries-input', 'value')]
)
def create_stories(n_clicks, project, epic, sprint, labels, summaries):
    if n_clicks == 0:
        return ""
    
    if not project or not summaries:
        return "Project and story summaries are required."

    summaries_list = summaries.strip().split('\n')
    labels_list = [label.strip() for label in labels.split(',')] if labels else []

    url = projects_df.loc[projects_df['project_name'] == project, 'url'].values[0]
    created_stories = []
    errors = []

    for summary in summaries_list:
        data = {
            "fields": {
                "project": {
                    "key": project
                },
                "summary": summary,
                "issuetype": {
                    "name": "Story"
                },
                "labels": labels_list
            }
        }

        if epic:
            data["fields"]["customfield_10011"] = epic  # Replace customfield_10011 with the actual field ID for epic link

        if sprint:
            data["fields"]["customfield_10007"] = sprint  # Replace customfield_10007 with the actual field ID for sprint

        response = requests.post(f'{url}/rest/api/2/issue', json=data, auth=auth)
        if response.status_code == 201:
            created_stories.append(f'Created: {summary}')
        else:
            errors.append(f'Error creating {summary}: {response.content}')

    result = []
    if created_stories:
        result.append(html.Div(f"Successfully created stories:", style={'color': 'green'}))
        result.extend([html.Div(story) for story in created_stories])
    if errors:
        result.append(html.Div(f"Errors occurred:", style={'color': 'red'}))
        result.extend([html.Div(error) for error in errors])

    return result

if __name__ == '__main__':
    app.run_server(debug=True)

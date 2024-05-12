import dash
from dash import dcc, html, Input, Output, DataTable
import pandas as pd
from jira import JIRA
import plotly.graph_objs as go

# Initialize Dash app
app = dash.Dash(__name__)

# Jira credentials
JIRA_SERVER = 'Your Jira Server URL'
JIRA_USERNAME = 'Your Jira Username'
JIRA_PASSWORD = 'Your Jira Password'

# Initialize Jira client
jira = JIRA(JIRA_SERVER, basic_auth=(JIRA_USERNAME, JIRA_PASSWORD))

# Get list of assignees
def get_assignees():
    assignees = []
    issues = jira.search_issues('', maxResults=0)
    for issue in issues:
        if issue.fields.assignee:
            assignees.append(issue.fields.assignee.displayName)
    assignees = list(set(assignees))  # Remove duplicates
    return assignees

# Dash layout
app.layout = html.Div([
    html.H1("Jira Issues by Assignee"),
    dcc.Dropdown(
        id='assignee-dropdown',
        options=[{'label': assignee, 'value': assignee} for assignee in get_assignees()],
        placeholder='Select an Assignee'
    ),
    html.Button('Search', id='search-btn', n_clicks=1),
    html.Div(id='datatable-container'),
    dcc.Graph(id='bar-chart'),
    dcc.Graph(id='pie-chart')
])

# Dash callback to fetch and filter issues
@app.callback(
    [Output('datatable-container', 'children'),
     Output('bar-chart', 'figure'),
     Output('pie-chart', 'figure')],
    [Input('search-btn', 'n_clicks')],
    [State('assignee-dropdown', 'value')]
)
def fetch_and_filter_issues(n_clicks, assignee):
    if n_clicks == 0:
        return None, {}, {}
    
    if not assignee:
        return html.Div("Please select an assignee."), {}, {}
    
    try:
        # Fetch issues for the selected assignee
        jql_assignee = f'assignee = "{assignee}"'
        issues_assignee = jira.search_issues(jql_assignee)
        
        if not issues_assignee:
            return html.Div(f"No issues found for assignee '{assignee}'."), {}, {}
        
        # Convert issues data to DataFrame
        issue_data = []
        for issue in issues_assignee:
            issue_data.append({
                "Key": issue.key,
                "Summary": issue.fields.summary,
                "Status": issue.fields.status.name,
                "Assignee": issue.fields.assignee.displayName if issue.fields.assignee else "Unassigned"
            })
        df = pd.DataFrame(issue_data)
        
        # Render DataTable
        datatable = DataTable(
            id='datatable',
            columns=[{"name": i, "id": i} for i in df.columns],
            data=df.to_dict('records')
        )
        
        # Create bar chart based on assignee
        assignee_counts = df['Summary'].groupby(df['Assignee']).count()
        bar_chart = go.Figure(data=[go.Bar(x=assignee_counts.index, y=assignee_counts.values)])
        bar_chart.update_layout(title=f'Issue Count by Assignee: {assignee}')
        
        # Fetch all issues for status distribution
        jql_status = ''
        issues_status = jira.search_issues(jql_status)
        
        if not issues_status:
            return datatable, bar_chart, {}
        
        # Convert issues data to DataFrame
        issue_status_data = []
        for issue in issues_status:
            issue_status_data.append({
                "Key": issue.key,
                "Summary": issue.fields.summary,
                "Status": issue.fields.status.name,
                "Assignee": issue.fields.assignee.displayName if issue.fields.assignee else "Unassigned"
            })
        df_status = pd.DataFrame(issue_status_data)
        
        # Create pie chart based on status
        status_counts = df_status['Status'].value_counts()
        pie_chart = go.Figure(data=[go.Pie(labels=status_counts.index, values=status_counts.values)])
        pie_chart.update_layout(title='Issue Status Distribution')
        
        return datatable, bar_chart, pie_chart
    except Exception as e:
        return html.Div(f"An error occurred: {str(e)}"), {}, {}

if __name__ == '__main__':
    app.run_server(debug=True)

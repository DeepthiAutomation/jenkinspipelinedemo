import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output
import dash_bootstrap_components as dbc
from pages import stories, backlogs

# Initialize the Dash app
app = dash.Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP], suppress_callback_exceptions=True)
server = app.server  # Expose the server variable for gunicorn

# Home Page Layout
home_layout = html.Div([
    html.H1("Welcome to JIRA Dashboard", style={'textAlign': 'center', 'fontFamily': 'Arial, sans-serif'}),
    html.Div([
        dcc.Link('Get Stories', href='/stories', className='btn btn-success', style={'marginRight': '10px'}),
        dcc.Link('Get Backlogs', href='/backlogs', className='btn btn-success')
    ], style={'textAlign': 'center', 'padding': '20px'})
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
        return stories.layout
    elif pathname == '/backlogs':
        return backlogs.layout
    else:
        return home_layout

if __name__ == '__main__':
    app.run_server(debug=True)

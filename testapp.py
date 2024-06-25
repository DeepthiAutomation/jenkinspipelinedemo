import dash
import dash_html_components as html
import dash_core_components as dcc

# Initialize the Dash app
app = dash.Dash(__name__)

# Define the layout
app.layout = html.Div(
    style={
        'fontFamily': 'Arial, sans-serif',
        'backgroundImage': 'url("https://www.toptal.com/designers/subtlepatterns/patterns/memphis-mini.png")',
        'height': '100vh',
        'margin': 0,
        'padding': 0,
    },
    children=[
        html.Header(
            style={
                'backgroundColor': '#4CAF50',
                'width': '100%',
                'padding': '20px',
                'color': 'white',
                'textAlign': 'center',
                'fontSize': '30px',
                'fontWeight': 'bold',
                'boxShadow': '0 4px 8px rgba(0, 0, 0, 0.1)',
                'position': 'fixed',
                'top': 0,
                'zIndex': 1000,
            },
            children='Welcome to Centralized Jira Insights Dashboard'
        ),
        html.Div(
            style={
                'display': 'flex',
                'flexDirection': 'column',
                'alignItems': 'center',
                'marginTop': '80px'  # Adjust margin to ensure buttons are below the fixed header
            },
            children=[
                html.Button('Generate My Current Sprint Dashboard', id='button-1', style={'margin': '10px', 'padding': '10px 20px', 'fontSize': '16px', 'backgroundColor': '#0AA3CF', 'color': 'white', 'border': 'none', 'borderRadius': '5px'}),
                html.Button('Generate My Backlog Dashboard', id='button-2', style={'margin': '10px', 'padding': '10px 20px', 'fontSize': '16px', 'backgroundColor': '#0AA3CF', 'color': 'white', 'border': 'none', 'borderRadius': '5px'}),
                html.Button('Generate My Quarterly, Yearly Reports', id='button-3', style={'margin': '10px', 'padding': '10px 20px', 'fontSize': '16px', 'backgroundColor': '#0AA3CF', 'color': 'white', 'border': 'none', 'borderRadius': '5px'}),
                html.Button('Assist me with Bulk Requests ', id='button-4', style={'margin': '10px', 'padding': '10px 20px', 'fontSize': '16px', 'backgroundColor': '#0AA3CF', 'color': 'white', 'border': 'none', 'borderRadius': '5px'}),
            ]
        )
    ]
)

# Run the app
if __name__ == '__main__':
    app.run_server(debug=True)

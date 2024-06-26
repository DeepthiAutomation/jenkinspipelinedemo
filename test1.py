import dash
import dash_html_components as html

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
        'display': 'flex',
        'flexDirection': 'column',
        'alignItems': 'center',
        'justifyContent': 'center',
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
            children='Rounded Rectangle Buttons'
        ),
        html.Div(
            style={
                'marginTop': '80px',
                'width': '100%',
                'maxWidth': '400px',
                'display': 'flex',
                'flexDirection': 'column',
                'alignItems': 'center',
                'justifyContent': 'center',
            },
            children=[
                html.Button('Button 1', id='button-1', style={
                    'margin': '10px',
                    'padding': '15px 30px',
                    'fontSize': '16px',
                    'backgroundColor': '#007bff',
                    'color': 'white',
                    'border': 'none',
                    'borderRadius': '15px',
                    'width': '100%',
                    'textAlign': 'center'
                }),
                html.Button('Button 2', id='button-2', style={
                    'margin': '10px',
                    'padding': '15px 30px',
                    'fontSize': '16px',
                    'backgroundColor': '#007bff',
                    'color': 'white',
                    'border': 'none',
                    'borderRadius': '15px',
                    'width': '100%',
                    'textAlign': 'center'
                }),
                html.Button('Button 3', id='button-3', style={
                    'margin': '10px',
                    'padding': '15px 30px',
                    'fontSize': '16px',
                    'backgroundColor': '#007bff',
                    'color': 'white',
                    'border': 'none',
                    'borderRadius': '15px',
                    'width': '100%',
                    'textAlign': 'center'
                }),
                html.Button('Button 4', id='button-4', style={
                    'margin': '10px',
                    'padding': '15px 30px',
                    'fontSize': '16px',
                    'backgroundColor': '#007bff',
                    'color': 'white',
                    'border': 'none',
                    'borderRadius': '15px',
                    'width': '100%',
                    'textAlign': 'center'
                }),
                html.Button('Button 5', id='button-5', style={
                    'margin': '10px',
                    'padding': '15px 30px',
                    'fontSize': '16px',
                    'backgroundColor': '#007bff',
                    'color': 'white',
                    'border': 'none',
                    'borderRadius': '15px',
                    'width': '100%',
                    'textAlign': 'center'
                }),
            ]
        )
    ]
)

# Run the app
if __name__ == '__main__':
    app.run_server(debug=True)

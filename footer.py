html.Footer(
    style={
        'backgroundColor': '#4CAF50',
        'width': '100%',
        'padding': '20px',
        'color': 'white',
        'textAlign': 'center',
        'fontSize': '16px',
        'fontWeight': 'bold',
        'boxShadow': '0 -4px 8px rgba(0, 0, 0, 0.1)',
        'position': 'fixed',
        'bottom': 0,
        'zIndex': 1000,
        'display': 'flex',
        'justifyContent': 'center',
        'alignItems': 'center'
    },
    children=[
        html.Img(src='https://your-logo-url.com/logo.png', style={'height': '30px', 'marginRight': '10px'}),
        'Your Footer Text Here'
    ]
)

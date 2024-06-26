html.Header(
    style={
        'backgroundColor': '#4CAF50',
        'width': '100%',
        'padding': '20px',
        'color': 'white',
        'fontSize': '30px',
        'fontWeight': 'bold',
        'boxShadow': '0 4px 8px rgba(0, 0, 0, 0.1)',
        'position': 'fixed',
        'top': 0,
        'zIndex': 1000,
        'display': 'flex',
        'justifyContent': 'space-between',
        'alignItems': 'center'
    },
    children=[
        html.Div('Rectangular Boxes with Navy Blue Borders', style={'flexGrow': '1', 'textAlign': 'center'}),
        html.Div(
            html.Img(src='https://your-logo-url.com/logo.png', style={'height': '50px'}),
            style={'position': 'absolute', 'right': '20px'}
        )
    ]
)

import dash
from dash import dcc, html
from dash.dependencies import Input, Output

# Initialize the Dash app
app = dash.Dash(__name__)

# Define the layout of the app
app.layout = html.Div(
    style={'backgroundColor': '#ffffff', 'padding': '50px'},
    children=[
        html.H1(
            "File Upload Example",
            style={'textAlign': 'center', 'color': '#333333'}
        ),
        html.H2(
            "Please drag and drop your files below",
            style={'textAlign': 'center', 'color': '#666666'}
        ),
        dcc.Upload(
            id='upload-data',
            children=html.Div(
                ['Drag and Drop or ', html.A('Select Files')],
                style={
                    'textAlign': 'center',
                    'borderWidth': '2px',
                    'borderStyle': 'dashed',
                    'borderRadius': '5px',
                    'padding': '40px',
                    'cursor': 'pointer',
                    'color': '#999999'
                }
            ),
            multiple=True
        ),
        html.Div(id='output-data-upload'),
        html.Br(),
        html.Div(
            children=[
                html.Label("Input Box", style={'fontSize': '20px'}),
                dcc.Input(
                    id='input-box',
                    type='text',
                    style={'width': '100%', 'padding': '10px', 'fontSize': '18px'}
                )
            ],
            style={'textAlign': 'center', 'marginTop': '20px'}
        )
    ]
)

# Define callback to process the uploaded files
@app.callback(
    Output('output-data-upload', 'children'),
    [Input('upload-data', 'contents')],
    [dash.dependencies.State('upload-data', 'filename'),
     dash.dependencies.State('upload-data', 'last_modified')]
)
def update_output(list_of_contents, list_of_names, list_of_dates):
    if list_of_contents is not None:
        children = [
            html.Div([
                html.H5(filename),
                html.H6(datetime.datetime.fromtimestamp(date)),
                html.Hr(),
                # You can add more components here to display file contents
            ])
            for filename, date in zip(list_of_names, list_of_dates)
        ]
        return children

# Run the app
if __name__ == '__main__':
    app.run_server(debug=True)

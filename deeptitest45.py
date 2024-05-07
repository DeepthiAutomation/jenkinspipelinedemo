import dash
from dash import dcc, html, Input, Output
import pandas as pd
import plotly.express as px
import dash_table

# Load data
df = pd.read_csv('your_data.csv')

# Ensure 'work' column is numeric
df['work'] = pd.to_numeric(df['work'], errors='coerce')

# Initialize Dash app
app = dash.Dash(__name__)

# Define layout
app.layout = html.Div(style={'backgroundImage': 'url("/assets/background_image.jpg")',
                             'backgroundRepeat': 'no-repeat',
                             'backgroundSize': 'cover',
                             'fontFamily': 'Arial, sans-serif',
                             'color': '#333333'}, children=[
    html.H1('Dashboard with Bar Chart and Pie Chart', style={'textAlign': 'center', 'marginBottom': '30px', 'fontSize': '36px'}),

    # Filter options
    html.Div([
        html.H2('Filter Data by Owner', style={'textAlign': 'center', 'fontSize': '24px'}),
        dcc.Dropdown(
            id='owner-filter',
            options=[{'label': owner, 'value': owner} for owner in df['owner'].unique()],
            value=df['owner'].unique()[0],  # Default value
            clearable=False,
            style={'width': '50%', 'margin': 'auto', 'backgroundColor': '#ffffff', 'color': '#333333', 'fontSize': '18px'}
        ),
    ], style={'marginBottom': '30px', 'padding': '20px', 'backgroundColor': '#ffffff', 'borderRadius': '10px'}),

    # Data table
    html.Div([
        html.H2('Data Table', style={'textAlign': 'center', 'fontSize': '24px'}),
        dash_table.DataTable(
            id='data-table',
            columns=[{'name': i, 'id': i} for i in df.columns],
            data=df.to_dict('records'),
            style_table={'overflowX': 'auto', 'backgroundColor': '#000000'},
            filter_action="native",
            page_size=8,
            style_header={'backgroundColor': '#000000', 'fontWeight': 'bold', 'color': '#ffffff', 'fontSize': '16px'},
            style_cell={
                'textAlign': 'left',
                'color': '#333333',
                'fontSize': '14px',
                'fontFamily': 'Arial, sans-serif',
                'backgroundColor': '#ffffff',
                'padding': '10px'
            },
            style_data_conditional=[
                {'if': {'row_index': 'odd'}, 'backgroundColor': 'rgb(245, 245, 245)'},
                {'if': {'column_id': 'owner'}, 'backgroundColor': 'rgb(255, 255, 153)'}  # Highlighting 'owner' column
            ],
        ),
    ], style={'marginBottom': '30px', 'padding': '20px', 'backgroundColor': '#ffffff', 'borderRadius': '10px'}),

    # Charts
    html.Div([
        # Bar chart
        html.Div([
            html.H2('Bar Chart - Sum of Work per Owner', style={'textAlign': 'center', 'fontSize': '24px'}),
            dcc.Graph(id='bar-chart', config={'displayModeBar': False}),
        ], style={'width': '45%', 'display': 'inline-block', 'marginTop': '50px', 'marginRight': '5%', 'marginLeft': '2%'}),

        # Pie chart
        html.Div([
            html.H2('Pie Chart - Distribution of Statuses', style={'textAlign': 'center', 'fontSize': '24px'}),
            dcc.Graph(id='pie-chart', config={'displayModeBar': False}),
        ], style={'width': '45%', 'display': 'inline-block', 'marginTop': '50px'}),
    ]),
])


# Callback to update charts based on filtered data
@app.callback(
    [Output('bar-chart', 'figure'),
     Output('pie-chart', 'figure')],
    [Input('owner-filter', 'value')]
)
def update_charts(owner_filter):
    filtered_df = df[df['owner'] == owner_filter]

    # Bar chart - Sum of work per owner
    work_sum_df = filtered_df.groupby('owner')['work'].sum().reset_index()  # Aggregate sum of work
    bar_fig = px.bar(work_sum_df, x='owner', y='work', title='Sum of Work per Owner',
                     labels={'owner': 'Owner', 'work': 'Sum of Work'}, color='owner', width=800, height=500)

    # Pie chart - Distribution of statuses
    status_counts = filtered_df['status'].value_counts().reset_index()
    status_counts.columns = ['status', 'count']
    pie_fig = px.pie(status_counts, names='status', values='count', title='Distribution of Statuses', width=800, height=500)

    return bar_fig, pie_fig.update_traces(textposition='inside', textinfo='percent+label')


if __name__ == '__main__':
    app.run_server(debug=True)

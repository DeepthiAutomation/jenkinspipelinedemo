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
app.layout = html.Div(style={'backgroundColor': '#f0f0f0', 'fontFamily': 'Arial, sans-serif'}, children=[
    html.H1('Dashboard with Bar Chart and Pie Chart', style={'textAlign': 'center', 'marginBottom': '30px', 'color': '#333333'}),

    # Filter options
    html.Div([
        html.H2('Filter Data by Owner', style={'textAlign': 'center', 'color': '#666666'}),
        dcc.Dropdown(
            id='owner-filter',
            options=[{'label': owner, 'value': owner} for owner in df['owner'].unique()],
            value=df['owner'].unique()[0],  # Default value
            clearable=False,
            style={'width': '50%', 'margin': 'auto', 'backgroundColor': '#ffffff', 'color': '#333333', 'fontFamily': 'Arial, sans-serif'}  # Reduce dropdown size
        ),
    ], style={'marginBottom': '30px', 'padding': '20px', 'backgroundColor': '#ffffff', 'borderRadius': '10px'}),

    # Charts
    html.Div([
        # Bar chart
        html.Div([
            html.H2('Bar Chart - Sum of Work per Owner', style={'textAlign': 'center', 'color': '#666666'}),
            dcc.Graph(id='bar-chart'),
        ], style={'width': '45%', 'display': 'inline-block', 'marginTop': '50px', 'marginRight': '5%'}),

        # Pie chart
        html.Div([
            html.H2('Pie Chart - Distribution of Statuses', style={'textAlign': 'center', 'color': '#666666'}),
            dcc.Graph(id='pie-chart'),
        ], style={'width': '45%', 'display': 'inline-block', 'marginTop': '50px'}),
    ]),

    # Data table
    html.Div([
        html.H2('Data Table', style={'textAlign': 'center', 'color': '#666666'}),
        dash_table.DataTable(
            id='data-table',
            columns=[{'name': i, 'id': i} for i in df.columns],
            data=df.to_dict('records'),
            style_table={'overflowX': 'auto'},
            filter_action="native",
            page_size=10,
            style_data_conditional=[
                {
                    'if': {'row_index': 'odd'},
                    'backgroundColor': 'rgb(248, 248, 248)'
                }
            ],
            style_header={
                'backgroundColor': 'rgb(230, 230, 230)',
                'fontWeight': 'bold'
            }
        ),
    ]),
])


# Callback to update charts based on filtered data
@app.callback(
    [Output('bar-chart', 'figure'),
     Output('pie-chart', 'figure'),
     Output('data-table', 'data')],
    [Input('owner-filter', 'value')]
)
def update_charts(owner_filter):
    filtered_df = df[df['owner'] == owner_filter]

    # Bar chart - Sum of work per owner
    work_sum_df = filtered_df.groupby('owner')['work'].sum().reset_index()  # Aggregate sum of work
    bar_fig = px.bar(work_sum_df, x='owner', y='work', title='Sum of Work per Owner',
                     labels={'owner': 'Owner', 'work': 'Sum of Work'}, color='owner')

    # Pie chart - Distribution of statuses
    status_counts = filtered_df['status'].value_counts().reset_index()
    status_counts.columns = ['status', 'count']
    pie_fig = px.pie(status_counts, names='status', values='count', title='Distribution of Statuses')

    return bar_fig, pie_fig.update_traces(textposition='inside', textinfo='percent+label'), filtered_df.to_dict('records')


if __name__ == '__main__':
    app.run_server(debug=True)

# Callback to update dropdown options dynamically
@app.callback(
    Output('table', 'dropdown'),
    [Input('interval-component', 'n_intervals')]
)
def update_dropdown(n):
    # Update the DataFrame with new data if needed
    # Here we're just reusing the existing data
    unique_categories = [{'label': category, 'value': category} for category in df['Category'].unique()]
    
    return {
        'Category': {
            'options': unique_categories
        }
    }

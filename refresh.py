import dash
from dash import dcc, html, Input, Output, State
import dash_table
import requests

# Sample API endpoint URLs
DEPARTMENTS_API_URL = "https://api.example.com/departments"
EMPLOYEES_API_URL = "https://api.example.com/employees"

# Initialize the Dash app
app = dash.Dash(__name__)

# Layout of the app
app.layout = html.Div([
    dcc.Dropdown(
        id='department-dropdown',
        placeholder="Select a department"
    ),
    dcc.Dropdown(
        id='employee-dropdown',
        placeholder="Select an employee ID"
    ),
    dash_table.DataTable(
        id='employee-table',
        columns=[],  # Columns will be populated dynamically
        data=[],  # Initial empty data
        style_table={'overflowX': 'auto'}
    )
])

# Callback to update the department dropdown options
@app.callback(
    Output('department-dropdown', 'options'),
    Input('department-dropdown', 'value')
)
def update_department_dropdown(_):
    # Fetch department data from the API
    response = requests.get(DEPARTMENTS_API_URL)

    if response.status_code == 200:
        departments = response.json()
        dropdown_options = [{'label': dept, 'value': dept} for dept in departments]
    else:
        dropdown_options = []

    return dropdown_options

# Callback to update the employee dropdown options and table
@app.callback(
    [Output('employee-dropdown', 'options'),
     Output('employee-table', 'data')],
    [Input('department-dropdown', 'value'),
     Input('employee-dropdown', 'value')],
    prevent_initial_call=True
)
def update_employee_dropdown_and_table(selected_department, selected_employee_id):
    if selected_department is None:
        return [], []

    # Fetch employee data from the API based on the selected department
    response = requests.get(EMPLOYEES_API_URL, params={'department': selected_department})

    if response.status_code == 200:
        employees = response.json()

        # Prepare dropdown options for employee IDs
        dropdown_options = [{'label': emp['Employee ID'], 'value': emp['Employee ID']} for emp in employees]

        # Check if a specific employee ID is selected
        if selected_employee_id:
            # Fetch employee data based on the selected employee ID
            selected_employee_data = next((emp for emp in employees if emp['Employee ID'] == selected_employee_id), None)
            if selected_employee_data:
                # Prepare data for the table
                table_data = [selected_employee_data]
            else:
                table_data = []
        else:
            table_data = []
    else:
        dropdown_options = []
        table_data = []

    return dropdown_options, table_data

# Run the app
if __name__ == '__main__':
    app.run_server(debug=True)

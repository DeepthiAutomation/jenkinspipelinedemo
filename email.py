from flask import Flask
import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output

# Step 1: Create the Flask server
server = Flask(__name__)

# Step 2: Create the Dash app
app = dash.Dash(__name__, server=server, url_base_pathname='/contact/')

# Step 3: Define the layout with a mailto link
app.layout = html.Div([
    html.H1("Contact Us"),
    html.P("Click the button below to send an email to test@gmail.com using your default email client."),
    html.A(
        html.Button('Send Email'),
        href="mailto:test@gmail.com?subject=Contact from Dash App&body=Hello, this is a test email!"
    )
])

# Step 4: Optionally, create a root endpoint for the Flask app
@server.route('/')
def home():
    return '''
    <h1>Welcome to the Multi-App Dashboard</h1>
    <p><a href="/contact/">Go to Contact Page</a></p>
    '''

# Step 5: Run the Flask server
if __name__ == '__main__':
    server.run(debug=True)

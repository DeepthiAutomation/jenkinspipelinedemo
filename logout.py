from datetime import timedelta
from flask import Flask, session

app = Flask(__name__)
app.secret_key = 'your_secret_key'

# Set session timeout to 10 minutes
app.permanent_session_lifetime = timedelta(minutes=10)

@app.before_request
def make_session_permanent():
    session.permanent = True

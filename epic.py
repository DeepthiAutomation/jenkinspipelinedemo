import requests
from requests.auth import HTTPBasicAuth
import json

# Replace these variables with your actual Jira details
jira_url = 'https://your-jira-instance.atlassian.net'
username = 'your-email@example.com'
api_token = 'your-api-token'
issue_key = 'ISSUE-123'  # The issue key you want to update

# API endpoint to update an issue
api_endpoint = f'{jira_url}/rest/api/3/issue/{issue_key}'

# Headers for the API request
headers = {
    'Accept': 'application/json',
    'Content-Type': 'application/json'
}

# Payload to remove the Epic link
payload = {
    "fields": {
        "customfield_10008": None  # Replace customfield_10008 with the actual field ID for the Epic Link in your Jira instance
    }
}

# Make the API request
response = requests.put(
    api_endpoint,
    headers=headers,
    auth=HTTPBasicAuth(username, api_token),
    data=json.dumps(payload)
)

# Check the response
if response.status_code == 204:
    print("Epic link removed successfully.")
else:
    print(f"Failed to remove Epic link: {response.status_code}")
    print(response.text)

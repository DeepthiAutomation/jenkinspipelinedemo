
import requests

# Define your Jira API URLs
jira_urls = [
    "https://your-jira-instance.com/rest/api/latest/search?jql=project=PROJECT1",
    "https://your-jira-instance.com/rest/api/latest/search?jql=project=PROJECT2",
    # Add more URLs for other projects or filters
]

# Function to fetch issues from Jira API
def fetch_jira_issues(url):
    try:
        response = requests.get(url)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        print("Error fetching data:", e)
        return None

# Fetch issues from each Jira URL
for url in jira_urls:
    data = fetch_jira_issues(url)
    if data:
        issues = data.get('issues', [])
        for issue in issues:
            key = issue.get('key')
            summary = issue.get('fields', {}).get('summary')
            status = issue.get('fields', {}).get('status', {}).get('name')
            print(f"Issue Key: {key}, Summary: {summary}, Status: {status}")
    else:
        print("No data returned from the API.")

# You can further process this data to create a dashboard using matplotlib or plotly for visualization

import requests
import csv

def execute_jql_query(jql, username, api_token):
    url = "https://your-jira-instance.atlassian.net/rest/api/3/search"
    headers = {
        "Accept": "application/json",
    }
    auth = (username, api_token)
    params = {
        "jql": jql,
        "maxResults": 1000  # Adjust as needed based on your requirement
    }
    response = requests.get(url, headers=headers, params=params, auth=auth)
    return response.json()

def convert_json_to_csv(json_data, csv_file):
    issues = json_data['issues']
    with open(csv_file, 'w', newline='', encoding='utf-8') as file:
        writer = csv.writer(file)
        # Write CSV header
        writer.writerow(['Key', 'Summary', 'Assignee', 'Status', 'Sprint'])  # Add 'Sprint' field
        for issue in issues:
            key = issue['key']
            summary = issue['fields']['summary']
            assignee = issue['fields']['assignee']['displayName'] if issue['fields']['assignee'] else ''
            status = issue['fields']['status']['name']
            sprint = issue['fields']['customfield_XXXXX'][0]['name'] if issue['fields'].get('customfield_XXXXX') else ''  # Replace XXXXX with the actual field ID for Sprint
            writer.writerow([key, summary, assignee, status, sprint])  # Add 'sprint' to the writerow

# Example usage:
jql_query = 'project = "YOUR_PROJECT_KEY" AND sprint in openSprints()'  # Adjust the JQL query to include Sprint
csv_file = 'jira_data.csv'  # Output CSV file name
username = 'your_username'
api_token = 'your_api_token'

# Execute the JQL query
json_data = execute_jql_query(jql_query, username, api_token)

# Convert JSON data to CSV
convert_json_to_csv(json_data, csv_file)

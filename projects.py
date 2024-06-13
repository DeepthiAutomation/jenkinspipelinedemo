import requests
from requests.auth import HTTPBasicAuth
import sqlite3

# Configuration for multiple Jira instances
JIRA_INSTANCES = {
    'Jira1': {
        'url': 'https://jira1-domain.atlassian.net',
        'email': 'your_email1',
        'api_token': 'your_api_token1',
    },
    'Jira2': {
        'url': 'https://jira2-domain.atlassian.net',
        'email': 'your_email2',
        'api_token': 'your_api_token2',
    }
}

# Function to fetch Jira projects
def fetch_jira_projects(jira_url, email, api_token):
    url = f"{jira_url}/rest/api/2/project"
    auth = HTTPBasicAuth(email, api_token)
    headers = {"Accept": "application/json"}
    response = requests.get(url, headers=headers, auth=auth)
    
    if response.status_code == 200:
        return response.json()
    else:
        print(f"Failed to fetch projects from {jira_url}: {response.status_code}")
        return None

# Function to create SQLite database and table
def create_database(db_name="jira_projects.db"):
    conn = sqlite3.connect(db_name)
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS projects (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            url TEXT,
            project_id TEXT,
            project_name TEXT
        )
    ''')
    conn.commit()
    conn.close()

# Function to store projects in SQLite database
def store_projects_in_db(projects, jira_url, db_name="jira_projects.db"):
    conn = sqlite3.connect(db_name)
    cursor = conn.cursor()
    for project in projects:
        cursor.execute('''
            INSERT INTO projects (url, project_id, project_name) 
            VALUES (?, ?, ?)
        ''', (jira_url, project['id'], project['name']))
    conn.commit()
    conn.close()

# Function to fetch and store projects from all Jira instances
def fetch_and_store_all_projects():
    create_database()
    for jira_instance, config in JIRA_INSTANCES.items():
        projects = fetch_jira_projects(config['url'], config['email'], config['api_token'])
        if projects:
            store_projects_in_db(projects, config['url'])

if __name__ == "__main__":
    fetch_and_store_all_projects()

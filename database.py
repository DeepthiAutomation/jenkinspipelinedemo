import requests

# Function to fetch and store projects
def fetch_and_store_projects(jira_url, auth):
    projects_url = f'{jira_url}/rest/api/2/project'
    response = requests.get(projects_url, auth=auth)
    projects = response.json()
    
    conn = sqlite3.connect('jira_dashboard.db')
    cursor = conn.cursor()
    
    # Truncate the projects table
    cursor.execute('DELETE FROM projects')
    
    for project in projects:
        cursor.execute('''
        INSERT INTO projects (url, project_id, project_name)
        VALUES (?, ?, ?)
        ''', (jira_url, project['id'], project['name']))
    
    conn.commit()
    conn.close()

# Function to fetch and store custom fields
def fetch_and_store_custom_fields(jira_url, auth):
    custom_fields_url = f'{jira_url}/rest/api/2/field'
    response = requests.get(custom_fields_url, auth=auth)
    fields = response.json()
    
    conn = sqlite3.connect('jira_dashboard.db')
    cursor = conn.cursor()
    
    # Truncate the custom_fields table
    cursor.execute('DELETE FROM custom_fields')
    
    for field in fields:
        cursor.execute('''
        INSERT INTO custom_fields (url, field_id, field_name)
        VALUES (?, ?, ?)
        ''', (jira_url, field['id'], field['name']))
    
    conn.commit()
    conn.close()

# Example usage
jira_urls = ['https://jira.example.com']
auth = ('username', 'password')

for url in jira_urls:
    fetch_and_store_projects(url, auth)
    fetch_and_store_custom_fields(url, auth)

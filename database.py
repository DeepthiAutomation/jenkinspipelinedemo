import sqlite3

# Connect to SQLite database (or create it if it doesn't exist)
conn = sqlite3.connect('jira_dashboard.db')
cursor = conn.cursor()

# Create tables
cursor.execute('''
CREATE TABLE IF NOT EXISTS projects (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    url TEXT,
    project_id TEXT,
    project_name TEXT
)
''')

cursor.execute('''
CREATE TABLE IF NOT EXISTS custom_fields (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    url TEXT,
    field_id TEXT,
    field_name TEXT
)
''')

conn.commit()
conn.close()

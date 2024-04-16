search_results = jira.search_issues('project=PROJECT AND assignee=currentUser()')
for issue in search_results:
    print("Issue Key:", issue.key)
    print("Issue Summary:", issue.fields.summary)

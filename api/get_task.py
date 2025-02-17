import requests
from config.config import headers
from api.retry import get_retry_session

session = get_retry_session()

def get_task(task_id):
    url = f'https://api.clickup.com/api/v2/task/{task_id}'
    response = session.get(url, headers=headers)
    return response.json()

def get_tasks(list_id, conditions=None):
    url = f'https://api.clickup.com/api/v2/list/{list_id}/task'
    params = {'include_closed': True}  # Include closed tasks
    if conditions:
        if 'tags' in conditions:
            params['tags[]'] = conditions['tags']
        if 'statuses' in conditions:
            params['statuses[]'] = conditions['statuses']
        if 'custom_field' in conditions:
            params['custom_fields'] = conditions['custom_field']
    response = session.get(url, headers=headers, params=params)
    return response.json()['tasks']



#get tasks for even closed tasks for both review folders and for final review folders
#similarly check for proper integration of review to video or graphi folder - status update

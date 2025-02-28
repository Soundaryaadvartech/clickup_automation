import requests
from config.config import headers
from api.retry import get_retry_session

session = get_retry_session()

def create_task(list_id, task_name, task_details):
    # Ensure due_date is an integer and add 1 day (86400000 ms)
    if 'due_date' in task_details:
        task_details['due_date'] = int(task_details['due_date'])  # Convert if string
        task_details['due_date'] += 86400000  # Add 1 day

    url = f'https://api.clickup.com/api/v2/list/{list_id}/task'
    payload = {
        'name': task_name,
        'description': task_details.get('description', ''),
        'tags': task_details.get('tags', []),
        'status': task_details.get('status', ''),
        'priority': task_details.get('priority', ''),
        'due_date': task_details.get('due_date', ''),
        'start_date': task_details.get('start_date', ''),
        'assignees': task_details.get('assignees', []),
        'custom_fields': task_details.get('custom_fields', [])
    }
    response = session.post(url, headers=headers, json=payload)
    return response.json()


def link_tasks(parent_task_id, child_task_id, link_type='dependency'):
    url = f'https://api.clickup.com/api/v2/task/{parent_task_id}/link/{child_task_id}'
    payload = {
        'link_type': link_type
    }
    response = session.post(url, headers=headers, json=payload)
    return response.json()
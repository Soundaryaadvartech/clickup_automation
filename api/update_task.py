import requests
from config.config import headers
from api.retry import get_retry_session

session = get_retry_session()

def update_task(task_id, update_params):
    url = f'https://api.clickup.com/api/v2/task/{task_id}'
    response = session.put(url, headers=headers, json=update_params)
    return response.json()
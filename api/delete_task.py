import requests
from config.config import headers
from api.retry import get_retry_session

session = get_retry_session()

def delete_task(task_id):
    url = f'https://api.clickup.com/api/v2/task/{task_id}'
    response = session.delete(url, headers=headers)
    return response.json()
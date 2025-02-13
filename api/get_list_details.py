import requests
from config.config import headers
from api.retry import get_retry_session

session = get_retry_session()

def get_list_details(list_id):
    url = f'https://api.clickup.com/api/v2/list/{list_id}'
    response = session.get(url, headers=headers)
    if response.status_code == 200:
        return response.json()
    else:
        print(f"Failed to fetch details for list {list_id}: {response.text}")
        return {}

def get_list_statuses(list_id):
    list_details = get_list_details(list_id)
    statuses = list_details.get('statuses', [])
    return statuses
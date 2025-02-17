import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

def get_retry_session():
    retry_strategy = Retry(
        total=30,  # Number of retries
        backoff_factor=1,  # Wait time between retries
        status_forcelist=[429, 500, 502, 503, 504],  # Retry on these status codes
        allowed_methods=["HEAD", "GET", "OPTIONS", "POST", "PUT", "DELETE"]  # Retry on these HTTP methods
    )
    adapter = HTTPAdapter(max_retries=retry_strategy)
    session = requests.Session()
    session.mount("https://", adapter)
    session.mount("http://", adapter)
    return session
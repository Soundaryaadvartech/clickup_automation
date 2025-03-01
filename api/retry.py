import logging
import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

# Configure logging for this script
logger = logging.getLogger('clickup_api_retry')
logger.setLevel(logging.INFO)
file_handler = logging.FileHandler('logs/clickup_api_retry.log')
formatter = logging.Formatter('%(asctime)s %(levelname)s %(message)s')
file_handler.setFormatter(formatter)
logger.addHandler(file_handler)

def get_retry_session():
    logger.info("Initializing retry session with custom retry strategy.")

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

    logger.info("Retry session successfully initialized.")
    return session
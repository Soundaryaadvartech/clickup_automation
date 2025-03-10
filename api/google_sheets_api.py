import gspread
from oauth2client.service_account import ServiceAccountCredentials
import logging
import time

# Configure logging for this script
logger = logging.getLogger('google_sheets_api')
logger.setLevel(logging.INFO)
file_handler = logging.FileHandler('logs/google_sheets_api.log')
formatter = logging.Formatter('%(asctime)s %(levelname)s %(message)s')
file_handler.setFormatter(formatter)
logger.addHandler(file_handler)
logger.propagate = False

# Define the scope and credentials for Google Sheets API
scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
creds = ServiceAccountCredentials.from_json_keyfile_name('/Users/ss/Downloads/Analytics/dataat.json', scope)
client = gspread.authorize(creds)

def update_google_sheet_bulk(sheet_url, tasks):
    try:
        sheet = client.open_by_url(sheet_url)
        worksheet = sheet.worksheet("Logs")
        
        for task in tasks:
            task_id = task['task_id']
            status = task['status']
            timestamp = task['timestamp']
            
            # Find the row with the task_id
            cell = worksheet.find(task_id)
            if cell:
                row = cell.row
                # Update status in column K (11th column)
                worksheet.update_cell(row, 11, status)
                
                # Determine where to put the timestamp based on status.
                # We compare status case-insensitively.
                if status.lower() == "in execution":
                    # Write timestamp in column M (13th column)
                    worksheet.update_cell(row, 13, timestamp)
                elif status.lower() == "to be scheduled":
                    # Write timestamp in column N (14th column)
                    worksheet.update_cell(row, 14, timestamp)
                
                logger.info(f"Updated task {task_id} in Google Sheet {sheet_url}")
            else:
                logger.warning(f"Task {task_id} not found in Google Sheet {sheet_url}")
    except Exception as e:
        logger.error(f"Failed to update Google Sheet {sheet_url} for tasks: {e}")
        raise

def update_google_sheet_bulk_with_retry(sheet_url, tasks, retries=30):
    for attempt in range(retries):
        try:
            update_google_sheet_bulk(sheet_url, tasks)
            break
        except Exception as e:
            logger.error(f"Attempt {attempt + 1} failed: {e}")
            if attempt < retries - 1:
                time.sleep(2 ** attempt)  # Exponential backoff
            else:
                logger.error(f"All {retries} attempts failed for tasks in Google Sheet {sheet_url}")
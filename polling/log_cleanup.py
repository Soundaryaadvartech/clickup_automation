import os
import time
import logging
from datetime import datetime, timedelta

# Configure logging for this script
logger = logging.getLogger('log_cleanup')
logger.setLevel(logging.INFO)
# Remove any existing handlers
if logger.hasHandlers():
    logger.handlers.clear()

file_handler = logging.FileHandler('logs/log_cleanup.log')
formatter = logging.Formatter('%(asctime)s %(levelname)s %(message)s')
file_handler.setFormatter(formatter)
logger.addHandler(file_handler)

# Disable propagation to avoid logging to the root logger
logger.propagate = False

def delete_old_log_records(log_dir='logs', days=2):
    logger.info(f"Starting log cleanup for log entries older than {days} days in directory: {log_dir}")
    now = datetime.now()
    cutoff = now - timedelta(days=days)

    for filename in os.listdir(log_dir):
        filepath = os.path.join(log_dir, filename)
        if os.path.isfile(filepath):
            try:
                with open(filepath, 'r') as file:
                    lines = file.readlines()
                
                with open(filepath, 'w') as file:
                    for line in lines:
                        try:
                            log_time_str = line.split(' ')[0] + ' ' + line.split(' ')[1]
                            log_time = datetime.strptime(log_time_str, '%Y-%m-%d %H:%M:%S,%f')
                            if log_time >= cutoff:
                                file.write(line)
                        except ValueError:
                            # If the line doesn't match the expected format, keep it
                            file.write(line)
                logger.info(f"Cleaned up old log entries in file: {filepath}")
            except Exception as e:
                logger.error(f"Error processing file {filepath}: {e}")

    logger.info("Finished log cleanup")


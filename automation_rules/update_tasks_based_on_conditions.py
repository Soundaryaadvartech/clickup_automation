import logging
from api.get_task import get_tasks
from api.update_task import update_task
from mysql.database import get_tasks_by_conditions, add_tasks_bulk, update_tasks_bulk

# Configure logging for this script
logger = logging.getLogger('update_tasks_based_on_conditions')
logger.setLevel(logging.INFO)

# Remove any existing handlers
if logger.hasHandlers():
    logger.handlers.clear()

file_handler = logging.FileHandler('logs/update_tasks_based_on_conditions.log')
formatter = logging.Formatter('%(asctime)s %(levelname)s %(message)s')
file_handler.setFormatter(formatter)
logger.addHandler(file_handler)

# Disable propagation to avoid logging to the root logger
logger.propagate = False

def update_tasks_based_on_conditions(list_ids, conditions, update_params):
    tasks_to_add = []
    tasks_to_update = []

    # Fetch existing tasks from the database for all list IDs
    existing_tasks = get_tasks_by_conditions(list_ids=list_ids)
    existing_task_ids = {task['task_id'] for task in existing_tasks}

    for list_id in list_ids:
        # Fetch tasks based on conditions
        tasks = get_tasks(list_id, conditions)

        all_task_ids = [task['id'] for task in tasks]
        logger.info(f"Successfully fetched {len(tasks)} tasks in list {list_id}: {all_task_ids}")

        for task in tasks:
            task_id = task['id']

            if task_id not in existing_task_ids:
                # Create a new entry in the database with default link_id
                tasks_to_add.append((task_id, "123456", "in progress", list_id, ",".join(tag['name'] for tag in task['tags']), task['name']))
                logger.info(f"Appending task {task_id} to bulk update to the database with default link_id 123456 in list {list_id}")

            # Update the task in ClickUp
            response = update_task(task_id, update_params)

            if 'err' in response:
                logger.error(f"Failed to update task {task_id} in list {list_id}: {response['err']} in clickup")
            else:
                logger.info(f"Successfully updated task {task_id} in list {list_id} to status {update_params['status']} in clickup")
                # Prepare the task for bulk update in the database
                tasks_to_update.append({'status': update_params['status'], 'task_id': task_id})

    # Bulk add new tasks to the database
    if tasks_to_add:
        logger.info(f"Tasks to add: {len(tasks_to_add)} in database")
        add_tasks_bulk(tasks_to_add)

    # Bulk update tasks in the database
    if tasks_to_update:
        logger.info(f"Tasks to update: {len(tasks_to_update)} in database")
        update_tasks_bulk(tasks_to_update, ['status'])

    logger.info(f"Processed {len(tasks_to_update)} tasks.")
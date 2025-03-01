import logging
from api.get_task import get_tasks
from api.update_task import update_task
from mysql.database import get_tasks_by_conditions, update_tasks_bulk

# Configure logging for this script
logger = logging.getLogger('update_linked_tasks_backward')
logger.setLevel(logging.INFO)

# Remove any existing handlers
if logger.hasHandlers():
    logger.handlers.clear()

file_handler = logging.FileHandler('logs/update_linked_tasks_backward.log')
formatter = logging.Formatter('%(asctime)s %(levelname)s %(message)s')
file_handler.setFormatter(formatter)
logger.addHandler(file_handler)

# Disable propagation to avoid logging to the root logger
logger.propagate = False

def update_linked_tasks_backward(list_ids, conditions, update_params):
    all_task_ids = []
    tasks_by_list_id = {}
    tasks_to_update_in_db = []
    linked_tasks_to_update = []
    for list_id in list_ids:
        tasks = get_tasks(list_id, conditions)
        tasks_by_list_id[list_id] = tasks
        for task in tasks:
            task_id = task['id']
            all_task_ids.append(task_id)

    # Fetch tasks from the database for the given list IDs
    existing_tasks = get_tasks_by_conditions(list_ids=list_ids)
    existing_tasks_by_id = {task['task_id']: task for task in existing_tasks}

    for list_id, tasks in tasks_by_list_id.items():
        logger.info(f"Processing List ID: {list_id} | Conditions: {conditions['statuses']} | Target Status: {update_params['status']}")
        for task in tasks:
            task_id = task['id']
            logger.info(f"Processing Task ID: {task_id} in List ID: {list_id}")
            if task_id in existing_tasks_by_id:
                db_task = existing_tasks_by_id[task_id]
                clickup_status = task['status']['status']

                logger.info(f"Task ID: {task_id} - ClickUp status: {clickup_status}, DB status: {db_task['status']}")

                if clickup_status != db_task['status']:
                    # Update the status in the database
                    tasks_to_update_in_db.append({
                        'status': clickup_status,
                        'task_id': task_id
                    })
                    logger.info(f"Task ID: {task_id} - Appending status update to DB: {clickup_status}")

                    # Fetch the linked task ID from the database
                    linked_task_id = db_task.get('link_id')  # Using .get() to avoid KeyError

                    if linked_task_id:
                        linked_tasks_to_update.append({
                            'linked_task_id': linked_task_id,
                            'status': update_params['status'],  # Use dynamic status from update_params
                            'description': task['description']
                        })
                        logger.info(f"Task ID: {task_id} - Linked Task ID: {linked_task_id} will be updated to {update_params['status']}")
                    else:
                        logger.warning(f"Task ID: {task_id} - No linked task ID found in DB.")
                else:
                    logger.debug(f"Task ID: {task_id} - Status unchanged, no update required.")


    # Update the status in the database for tasks that have different statuses
    if tasks_to_update_in_db:
        logger.info(f"Updating {len(tasks_to_update_in_db)} task(s) status in the database.")
        update_tasks_bulk(tasks_to_update_in_db, ['status'])

    # Update the status and description in ClickUp for the linked tasks
    for linked_task in linked_tasks_to_update:
        linked_task_id = linked_task['linked_task_id']
        update_params = {
            'status': linked_task['status'],
            'description': linked_task['description']
        }

        logger.info(f"Updating linked task ID: {linked_task_id} in ClickUp with status: {update_params['status']}")
        
        response = update_task(linked_task_id, update_params)
        
        if 'err' in response:
            logger.error(f"Failed to update linked task {linked_task_id}: {response['err']} in clickup")
        else:
            logger.info(f"Successfully updated linked task {linked_task_id} in clickup to status: {update_params['status']}")

    # Update the status of the linked tasks in the database in bulk
    if linked_tasks_to_update:
        linked_tasks_to_update_db = [
            {'task_id': linked_task['linked_task_id'], 'status': linked_task['status']}
            for linked_task in linked_tasks_to_update
        ]

        logger.info(f"Updating {len(linked_tasks_to_update_db)} linked task(s) status in the database.")
        update_tasks_bulk(linked_tasks_to_update_db, ['status'])

    logger.info(f"Processed {len(linked_tasks_to_update)} linked task(s).")

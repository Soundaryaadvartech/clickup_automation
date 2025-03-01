import logging
from api.get_task import get_tasks
from api.update_task import update_task
from mysql.database import get_tasks_by_conditions, update_tasks_bulk

# Configure logging for this script
logger = logging.getLogger('update_linked_tasks_forward')
logger.setLevel(logging.INFO)

# Remove any existing handlers
if logger.hasHandlers():
    logger.handlers.clear()

file_handler = logging.FileHandler('logs/update_linked_tasks_forward.log')
formatter = logging.Formatter('%(asctime)s %(levelname)s %(message)s')
file_handler.setFormatter(formatter)
logger.addHandler(file_handler)

# Disable propagation to avoid logging to the root logger
logger.propagate = False

def update_linked_tasks_forward(list_ids, conditions, update_params):
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

    # Fetch tasks from the database for the given link IDs
    link_ids = [task['task_id'] for task in existing_tasks]
    linked_tasks = get_tasks_by_conditions(link_ids=link_ids)
    linked_tasks_by_id = {task['link_id']: task for task in linked_tasks}

    # Collect unique list IDs for linked tasks
    linked_list_ids = list(set([task['list_id'] for task in linked_tasks]))

    # Fetch all linked tasks from ClickUp for the collected list IDs
    clickup_linked_tasks = {}
    for list_id in linked_list_ids:
        tasks = get_tasks(list_id)
        for task in tasks:
            clickup_linked_tasks[task['id']] = task

    for list_id, tasks in tasks_by_list_id.items():
        logger.info(f"Processing List ID: {list_id} | Conditions: {conditions['statuses']} | Target Status: {update_params['status']}")
        for task in tasks:
            task_id = task['id']
            logger.info(f"Processing Task ID: {task_id} in List ID: {list_id}")

            if task_id in existing_tasks_by_id:
                db_task = existing_tasks_by_id[task_id]
                clickup_status = task['status']['status']
                logger.info(f"Task ID: {task_id} | ClickUp Status: {clickup_status} | DB Status: {db_task['status']}")

                if clickup_status != db_task['status']:
                    tasks_to_update_in_db.append({'status': clickup_status, 'task_id': task_id})
                    logger.info(f"→ Marking Task ID: {task_id} for DB status update to '{clickup_status}'")

                    if db_task['task_id'] in linked_tasks_by_id:
                        linked_task = linked_tasks_by_id[db_task['task_id']]
                        linked_task_id = linked_task['task_id']

                        if linked_task_id in clickup_linked_tasks:
                            linked_task_status = clickup_linked_tasks[linked_task_id]['status']['status']

                            if linked_task_status != "complete":
                                linked_tasks_to_update.append({
                                    'linked_task_id': linked_task_id,
                                    'status': update_params['status'],
                                    'description': task['description']
                                })
                                logger.info(f"→ Updating Linked Task ID: {linked_task_id} to '{update_params['status']}'")

                            else:
                                tasks_to_update_in_db.append({'status': "complete", 'task_id': linked_task_id})
                                logger.info(f"✔ Linked Task ID: {linked_task_id} already 'complete' - Marking as complete in DB")


    # Update the status in the database for tasks that have different statuses
    if tasks_to_update_in_db:
        logger.info(f"Updating {len(tasks_to_update_in_db)} tasks in the database.")
        update_tasks_bulk(tasks_to_update_in_db, ['status'])

    # Update the status and description in ClickUp for the linked tasks
    for linked_task in linked_tasks_to_update:
        linked_task_id = linked_task['linked_task_id']
        update_params = {
            'status': linked_task['status'],
            'description': linked_task['description']
        }
        response = update_task(linked_task_id, update_params)
        
        if 'err' in response:
            logger.error(f"Failed to update linked task {linked_task_id}: {response['err']} in clickup")
        else:
            logger.info(f"Updated linked task {linked_task_id} to status '{linked_task['status']}' in ClickUp")

    # Update the status of the linked tasks in the database in bulk
    if linked_tasks_to_update:
        linked_tasks_to_update_db = [
            {'task_id': linked_task['linked_task_id'], 'status': linked_task['status']}
            for linked_task in linked_tasks_to_update
        ]
        logger.info(f"Updating {len(linked_tasks_to_update_db)} linked tasks in the database.")
        update_tasks_bulk(linked_tasks_to_update_db, ['status'])

    logger.info(f"Finished processing {len(linked_tasks_to_update)} linked tasks.")

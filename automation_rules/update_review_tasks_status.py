import logging
from api.get_task import get_tasks
from api.update_task import update_task
from mysql.database import get_tasks_by_conditions, update_tasks_bulk

# Configure logging for this script
logger = logging.getLogger('update_review_tasks_status')
logger.setLevel(logging.INFO)

# Remove any existing handlers
if logger.hasHandlers():
    logger.handlers.clear()

file_handler = logging.FileHandler('logs/update_review_tasks_status.log')
formatter = logging.Formatter('%(asctime)s %(levelname)s %(message)s')
file_handler.setFormatter(formatter)
logger.addHandler(file_handler)

# Disable propagation to avoid logging to the root logger
logger.propagate = False

def update_review_tasks_status(list_ids, conditions, update_params):
    tasks_to_update = []

    # Fetch existing review tasks from the database for all list IDs
    existing_tasks = get_tasks_by_conditions(list_ids=list_ids, statuses=conditions['statuses'])
    existing_task_ids = {task['task_id'] for task in existing_tasks}

    # Initialize linked_tasks as an empty list
    linked_tasks = []

    # Fetch tasks from the database for all link IDs
    if existing_task_ids:
        linked_tasks = get_tasks_by_conditions(link_ids=list(existing_task_ids))
        linked_tasks_by_link_id = {}
        for task in linked_tasks:
            if task['link_id'] not in linked_tasks_by_link_id:
                linked_tasks_by_link_id[task['link_id']] = []
            linked_tasks_by_link_id[task['link_id']].append(task)
    else:
        linked_tasks_by_link_id = {}

    # Collect all list IDs for existing tasks and linked tasks
    all_list_ids = list(set(list_ids + [task['list_id'] for task in linked_tasks]))

    # Fetch all tasks from ClickUp for the collected list IDs
    clickup_tasks = {}
    for list_id in all_list_ids:
        tasks = get_tasks(list_id)
        for task in tasks:
            clickup_tasks[task['id']] = task

    for task in existing_tasks:
        task_id = task['task_id']
    
        if task_id in linked_tasks_by_link_id:
            logger.info(f"Processing task ID: {task_id}, found linked tasks.")
            
            for linked_task in linked_tasks_by_link_id[task_id]:
                linked_task_id = linked_task['task_id']

                # Fetch the status of the linked task from ClickUp
                #logger.info(f"Fetching status of linked task ID: {linked_task_id} from ClickUp.")
                linked_task_status = clickup_tasks[linked_task_id]['status']['status']
                logger.info(f"Linked task ID: {linked_task_id} has status: {linked_task_status}")

                if linked_task_status == "complete":
                    logger.info(f"Linked task {linked_task_id} is marked as complete.")
                    
                    # Fetch the status of the main task from ClickUp
                    task_status = clickup_tasks[task_id]['status']['status']
                    logger.info(f"Review Task ID {task_id} current clickup status: {task_status}")

                    if task_status != "complete":
                        # Update the status of the task in ClickUp to "complete"
                        update_params['status'] = "complete"
                        response = update_task(task_id, update_params)

                        if 'err' in response:
                            logger.error(f"Failed to update task {task_id} in list {list_id}: {response['err']} in clickup")
                        else:
                            logger.info(f"Successfully updated task {task_id} in list {list_id} to 'complete' in clickup")
                            tasks_to_update.append({'status': "complete", 'task_id': task_id})
                            logger.info(f"appending review {task_id} to update in database")

                    # Add both main task and linked task to the update list
                    tasks_to_update.append({'status': "complete", 'task_id': task_id})
                    logger.info(f"appending review {task_id} to update in database")
                    tasks_to_update.append({'status': "complete", 'task_id': linked_task_id})
                    logger.info(f"appending linked task {linked_task_id} to update in database")

        else:
            # Fetch the status of the task from ClickUp
            logger.info(f"Fetching status of task ID: {task_id} from ClickUp.")
            task_status = clickup_tasks[task_id]['status']['status']

            if task_status == "complete":
                logger.info(f"Task ID {task_id} is marked as complete. Adding to update list.")
                tasks_to_update.append({'status': "complete", 'task_id': task_id})

    # Bulk update tasks in the database
    if tasks_to_update:
        logger.info(f"Tasks to update: {len(tasks_to_update)} in database")
        update_tasks_bulk(tasks_to_update, ['status'])

    logger.info(f"Processed {len(tasks_to_update)} tasks.")
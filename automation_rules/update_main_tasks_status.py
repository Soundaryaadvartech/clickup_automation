import logging
from api.update_task import update_task
from mysql.database import get_tasks_by_conditions, update_tasks_bulk

# Configure logging for this script
logger = logging.getLogger('update_main_tasks_status')
logger.setLevel(logging.INFO)

# Remove any existing handlers
if logger.hasHandlers():
    logger.handlers.clear()

file_handler = logging.FileHandler('logs/update_main_tasks_status.log')
formatter = logging.Formatter('%(asctime)s %(levelname)s %(message)s')
file_handler.setFormatter(formatter)
logger.addHandler(file_handler)

# Disable propagation to avoid logging to the root logger
logger.propagate = False

def update_main_tasks_status(list_ids, conditions, update_params):
    tasks_to_update = []

    # Fetch existing review tasks from the database for all list IDs
    existing_tasks = get_tasks_by_conditions(list_ids=list_ids, statuses=conditions['statuses'])
    existing_task_ids = {task['task_id'] for task in existing_tasks}

    # Fetch tasks from the database for all link IDs
    if existing_task_ids:
        linked_tasks = get_tasks_by_conditions(link_ids=list(existing_task_ids))
        linked_tasks_by_link_id = {}
        for task in linked_tasks:
            if task['link_id'] not in linked_tasks_by_link_id:
                linked_tasks_by_link_id[task['link_id']] = []
            linked_tasks_by_link_id[task['link_id']].append(task)
        
        if linked_tasks:
            # Fetch another list of tasks from the database based on the linked_task ids
            second_linked_task_ids = [task['task_id'] for task in linked_tasks]
            second_linked_tasks = get_tasks_by_conditions(link_ids=second_linked_task_ids)
            second_linked_tasks_by_id = {}
            for task in second_linked_tasks:
                if task['link_id'] not in second_linked_tasks_by_id:
                    second_linked_tasks_by_id[task['link_id']] = []
                second_linked_tasks_by_id[task['link_id']].append(task)

    for task in existing_tasks:
        task_id = task['task_id']
        logger.info(f"Processing task ID: {task_id}")

        all_linked_tasks_complete = True

        # Iterate over all linked tasks
        if task_id in linked_tasks_by_link_id:
            for linked_task in linked_tasks_by_link_id[task_id]:
                linked_task_id = linked_task['task_id']
                logger.debug(f"Checking first-level linked task: {linked_task_id} for task ID: {task_id}")

                # Check if linked task has second-level linked tasks
                if linked_task_id in second_linked_tasks_by_id:
                    for second_linked_task in second_linked_tasks_by_id[linked_task_id]:
                        second_linked_task_id = second_linked_task['task_id']
                        logger.debug(f"Checking second-level(review) linked task: {second_linked_task_id} for linked task: {linked_task_id}")

                        if second_linked_task['status'] != "complete":
                            logger.info(f"Second-level/Review linked task {second_linked_task_id} is not complete.")
                            all_linked_tasks_complete = False
                            break

                    if not all_linked_tasks_complete:
                        logger.info(f"Not all linked tasks are complete for task ID: {task_id}. Skipping update.")
                        break
                else:
                    # If second-level linked tasks are missing, mark as incomplete
                    logger.warning(f"No second-level(review) linked tasks found for linked task {linked_task_id}. Marking as incomplete.")
                    all_linked_tasks_complete = False
                    break

        if all_linked_tasks_complete:
            # Update the status of the task in ClickUp
            response = update_task(task_id, update_params)

            if 'err' in response:
                logger.error(f"Failed to update task {task_id} in ClickUp: {response['err']}")
            else:
                logger.info(f"Successfully updated task {task_id} in ClickUp to status: {update_params['status']}")
                # Add the task to the update list
                tasks_to_update.append({'status': update_params['status'], 'task_id': task_id})


    # Bulk update tasks in the database
    if tasks_to_update:
        logger.info(f"Tasks to update: {len(tasks_to_update)} in database")
        update_tasks_bulk(tasks_to_update, ['status'])

    logger.info(f"Processed {len(tasks_to_update)} tasks.")
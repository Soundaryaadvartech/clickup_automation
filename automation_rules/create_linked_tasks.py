import logging
from api.get_task import get_tasks
from api.update_task import update_task
from api.create_task import create_task, link_tasks
from api.get_list_details import get_list_statuses  # Import the function to get list statuses
from mysql.database import get_tasks_by_conditions, add_tasks_bulk
from config.linked_tasks_mapping import TAG_TO_LIST_ID_MAP, LIST_ID_TO_NAME_MAP, LIST_ID_TO_TAGS_MAP, REVIEW_FOLDER_LIST_IDS  # Import mappings

# Configure logging for this script
logger = logging.getLogger('create_linked_tasks')
logger.setLevel(logging.INFO)
# Remove any existing handlers
if logger.hasHandlers():
    logger.handlers.clear()

file_handler = logging.FileHandler('logs/create_linked_tasks.log')
formatter = logging.Formatter('%(asctime)s %(levelname)s %(message)s')
file_handler.setFormatter(formatter)
logger.addHandler(file_handler)

# Disable propagation to avoid logging to the root logger
logger.propagate = False

def create_linked_tasks(list_ids, conditions):
    all_task_ids = []
    new_tasks_to_add = []
    tasks_by_list_id = {}
     
    for list_id in list_ids:
        logger.info(f"Processing list ID: {list_id}")
        tasks = get_tasks(list_id, conditions)
        tasks_by_list_id[list_id] = tasks
        for task in tasks:
            task_id = task['id']
            all_task_ids.append(task_id)
            logger.info(f"Processing task ID: {task_id} in list ID: {list_id}")

    # Collect all target list IDs based on tags
    target_list_ids = set()
    for list_id in list_ids:
        conditional_tags = LIST_ID_TO_TAGS_MAP.get(list_id, [])
        for tag in conditional_tags:
            target_list_id = TAG_TO_LIST_ID_MAP.get(tag)
            if target_list_id:
                target_list_ids.add(target_list_id)

    # Fetch existing tasks for all target list IDs at once
    existing_tasks = get_tasks_by_conditions(list_ids=list(target_list_ids))
    existing_task_ids_by_list_id = {}
    for task in existing_tasks:
        if task['list_id'] not in existing_task_ids_by_list_id:
            existing_task_ids_by_list_id[task['list_id']] = set()
        existing_task_ids_by_list_id[task['list_id']].add(task['link_id'])

    for list_id, tasks in tasks_by_list_id.items():
        for task in tasks:
            task_id = task['id']
            # Determine the appropriate list IDs based on tags
            new_linked_task_ids = set()
            conditional_tags = LIST_ID_TO_TAGS_MAP.get(list_id, [])
            for tag in task['tags']:
                tag_name = tag['name'].lower()
                if tag_name in TAG_TO_LIST_ID_MAP and tag_name in conditional_tags:
                    linked_list_id = TAG_TO_LIST_ID_MAP[tag_name]
                    if task_id in existing_task_ids_by_list_id.get(linked_list_id, set()):
                        logger.info(f"Task {task_id} already has linked tasks in the target list {linked_list_id}, skipping creation.")
                        continue

                    logger.info(f"Creating linked task in list ID: {linked_list_id} for tag: {tag_name}")

                    # Fetch the available statuses for the target list
                    list_statuses = get_list_statuses(linked_list_id)
                    if list_statuses:
                        first_status = list_statuses[0]['status']
                    else:
                        first_status = 'to do'  # Fallback to 'to do' if no statuses are found
                    
                    # Add suffix to task name if the linked task is being created in a review folder
                    task_name = task['name']
                    if linked_list_id in REVIEW_FOLDER_LIST_IDS:
                        source_tag_name = LIST_ID_TO_NAME_MAP.get(list_id, tag_name)
                        task_name = f"{task_name} - {source_tag_name}"

                    task_details = {
                        'description': task['description'],
                        'tags': task['tags'],
                        'status': first_status,  # Set status to the first status in the list
                        'priority': task['priority'],
                        'due_date': task['due_date'],
                        'start_date': task['start_date'],
                        'assignees': task['assignees'],
                        'custom_fields': task['custom_fields']
                    }
                    
                    response = create_task(linked_list_id, task_name, task_details)
                    if 'err' in response:
                        logger.error(f"Failed to create linked task for {task_id} in list {linked_list_id}: {response['err']} in clickup")
                    else:
                        linked_task_id = response['id']
                        new_linked_task_ids.add(linked_task_id)
                        logger.info(f"Created linked task ID: {linked_task_id} for task ID: {task_id} in clickup")
                        link_response = link_tasks(task_id, linked_task_id)
                        if 'err' in link_response:
                            logger.error(f"Failed to link task {task_id} with {linked_task_id}: {link_response['err']} in clickup")
                        else:
                            logger.info(f"Successfully linked task {linked_task_id} for {task_id} in list {linked_list_id} in clickup")

                        # Add the new linked task to the list of tasks to add to the database
                        logger.info(f"Appending linked task {linked_task_id} {task_id} {first_status} {linked_list_id} {','.join(tag['name'] for tag in task['tags'])} to update in bulk to the database")
                        new_tasks_to_add.append((linked_task_id, task_id, first_status, linked_list_id, ",".join(tag['name'] for tag in task['tags']), task_name))

                        # Check if the original task status is "in approval" and update its name
                        if isinstance(task['status'], dict) and task['status'].get('status', '').lower() == "in approval":
                            updated_task_name = f"{task['name']} - FA"
                            update_task(task_id, {'name': updated_task_name})
                            logger.info(f"Updated task ID: {task_id} name to include 'FA' suffix.")

    # Bulk add new linked tasks to the database
    if new_tasks_to_add:
        logger.info(f"Adding {len(new_tasks_to_add)} new linked tasks to the database.")
        add_tasks_bulk(new_tasks_to_add)
    
    logger.info(f"Processed {len(new_tasks_to_add)} tasks.")
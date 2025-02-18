from api.get_task import get_tasks
from api.update_task import update_task
from mysql.database import get_tasks_by_conditions, update_tasks_bulk

def update_linked_tasks(list_ids, conditions, update_params):
    all_task_ids = []
    tasks_by_list_id = {}
    tasks_to_update_in_db = []
    linked_tasks_to_update = []
    print(f"reedit update_linked_tasks")
    for list_id in list_ids:
        print(f"Processing list ID: {list_id}")
        tasks = get_tasks(list_id, conditions)
        tasks_by_list_id[list_id] = tasks
        for task in tasks:
            task_id = task['id']
            all_task_ids.append(task_id)
            print(f"Processing task ID: {task_id} with tags: {task['tags']}")

    # Fetch tasks from the database for the given list IDs
    existing_tasks = get_tasks_by_conditions(list_ids=list_ids)
    existing_tasks_by_id = {task['task_id']: task for task in existing_tasks}

    for list_id, tasks in tasks_by_list_id.items():
        for task in tasks:
            task_id = task['id']
            if task_id in existing_tasks_by_id:
                db_task = existing_tasks_by_id[task_id]
                # Compare the status from ClickUp with the status in the database
                clickup_status = task['status']['status']
                print(f" task status in clickup {clickup_status} task status in db {db_task['status']}")
                if clickup_status != db_task['status']:
                    # Update the status in the database
                    tasks_to_update_in_db.append({
                        'status': clickup_status,
                        'task_id': task_id
                    })
                    # Fetch the linked task ID from the database
                    linked_task_id = db_task['link_id']
                    linked_tasks_to_update.append({
                        'linked_task_id': linked_task_id,
                        'status': update_params['status'],  # Use dynamic status from update_params
                        'description': task['description']
                    })

    # Update the status in the database for tasks that have different statuses
    if tasks_to_update_in_db:
        print(f"updating tasks status to db")
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
            print(f"Failed to update linked task {linked_task_id}: {response['err']}")
        else:
            print(f"Successfully updated linked task {linked_task_id}")

    # Update the status of the linked tasks in the database in bulk
    if linked_tasks_to_update:
        linked_tasks_to_update_db = [
            {'task_id': linked_task['linked_task_id'], 'status': linked_task['status']}
            for linked_task in linked_tasks_to_update
        ]
        update_tasks_bulk(linked_tasks_to_update_db, ['status'])

    print(f"Processed {len(linked_tasks_to_update)} linked tasks.")
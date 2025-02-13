from api.get_task import get_tasks
from api.update_task import update_task
from mysql.database import get_tasks_by_conditions, update_tasks_bulk

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
        tasks = get_tasks(list_id, conditions)
        for task in tasks:
            clickup_tasks[task['id']] = task

    for task in existing_tasks:
        task_id = task['task_id']
        if task_id in linked_tasks_by_link_id:
            print(f"Processing task ID: {task_id}")
            for linked_task in linked_tasks_by_link_id[task_id]:
                # Fetch the status of the linked task from ClickUp
                print(f"Fetching linked task {linked_task['task_id']} status from ClickUp")
                linked_task_status = clickup_tasks[linked_task['task_id']]['status']['status']
                print(f"Linked task status: {linked_task_status}")
                if linked_task_status == "complete":
                    print(f"Linked task {linked_task['task_id']} is complete.")
                    # Fetch the status of the task from ClickUp
                    task_status = clickup_tasks[task_id]['status']['status']
                    print(f"Task ID {task_id} status: {task_status}")
                    if task_status != "complete":
                        # Update the status of the task in ClickUp to "complete"
                        update_params['status'] = "complete"
                        response = update_task(task_id, update_params)
                        if 'err' in response:
                            print(f"Failed to update task {task_id} in list {list_id}: {response['err']}")
                        else:
                            print(f"Successfully updated task {task_id} in list {list_id}")
                            tasks_to_update.append({'status': "complete", 'task_id': task_id})
                    # Add the task to the update list
                    tasks_to_update.append({'status': "complete", 'task_id': task_id})
                    # Add the linked task to the update list
                    tasks_to_update.append({'status': "complete", 'task_id': linked_task['task_id']})
        else:
            # Fetch the status of the task from ClickUp
            print(f"Fetching task {task_id} status from ClickUp")
            task_status = clickup_tasks[task_id]['status']['status']
            if task_status == "complete":
                tasks_to_update.append({'status': "complete", 'task_id': task_id})

    # Bulk update tasks in the database
    if tasks_to_update:
        print(f"Tasks to update: {tasks_to_update}")
        update_tasks_bulk(tasks_to_update, ['status'])

    print(f"Processed {len(tasks_to_update)} tasks.")
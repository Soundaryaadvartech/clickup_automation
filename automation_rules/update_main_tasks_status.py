from api.update_task import update_task
from mysql.database import get_tasks_by_conditions, update_tasks_bulk

def update_main_tasks_status(list_ids, conditions, update_params):
    tasks_to_update = []

    # Fetch existing review tasks from the database for all list IDs
    print(f"Fetching tasks for list IDs: {list_ids}, conditions: {conditions}")
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
        print(f"Processing task ID: {task_id}")
        all_linked_tasks_complete = True

        # Iterate for all the task ids in linked_tasks_by_link_id
        if task_id in linked_tasks_by_link_id:
            for linked_task in linked_tasks_by_link_id[task_id]:
                print(f"first level all linked tasks {linked_task}")
                # Get the linked task id status from second linked tasks
                print(f"first level matching linked task id {task_id} and linked task {linked_task['task_id']}")
                if linked_task['task_id'] in second_linked_tasks_by_id:
                    for second_linked_task in second_linked_tasks_by_id[linked_task['task_id']]:
                        print(f"second linked task {second_linked_task}")
                        if second_linked_task['status'] != "complete":
                            all_linked_tasks_complete = False
                            break
                    if not all_linked_tasks_complete:
                        break
                else:
                    # If second linked task is not found, mark as incomplete and break
                    all_linked_tasks_complete = False
                    break

        if all_linked_tasks_complete:
            # Update the status of the task in ClickUp
            response = update_task(task_id, update_params)
            if 'err' in response:
                print(f"Failed to update task {task_id} in ClickUp: {response['err']}")
            else:
                print(f"Successfully updated task {task_id} in ClickUp")
                # Add the task to the update list
                tasks_to_update.append({'status': update_params['status'], 'task_id': task_id})

    # Bulk update tasks in the database
    if tasks_to_update:
        update_tasks_bulk(tasks_to_update, ['status'])

    print(f"Processed {len(tasks_to_update)} tasks.")
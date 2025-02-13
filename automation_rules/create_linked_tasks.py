from api.get_task import get_tasks
from api.create_task import create_task, link_tasks
from api.get_list_details import get_list_statuses  # Import the function to get list statuses
from mysql.database import get_tasks_by_conditions, add_tasks_bulk

# Define a mapping of tags to list IDs to create tasks based on tags
TAG_TO_LIST_ID_MAP = {
    'prabhu': '901606178743',
    'deepak': '901606178750',
    'nandhu': '901606248381',
    'abhijith': '901606186292',
    'vaibhav': '901606248361',
    'beelittle': '901606177816',
    'prathiksham': '901606248338',
    'zing': '901606248326',
    'adoreaboo': '901606248353',
    'all': '901606248206'
    # Add more mappings as needed
}

# Define a mapping of list IDs to conditional tags for creating linked tasks in relevant list id only based on tags
LIST_ID_TO_TAGS_MAP = {
    #socialmedia
    '901605050377': ['prabhu', 'deepak', 'abhijith', 'nandhu', 'vaibhav'], #beelittle
    '901606186307': ['prabhu', 'deepak', 'abhijith', 'nandhu', 'vaibhav'], #zing
    '901606186317': ['prabhu', 'deepak', 'abhijith', 'nandhu', 'vaibhav'], #prathiksham
    '901606186318': ['prabhu', 'deepak', 'abhijith', 'nandhu', 'vaibhav'], #adoreaboo
    #ads
    '901606186180': ['prabhu', 'deepak', 'abhijith', 'nandhu', 'vaibhav'], #beelittle 
    '901606186297': ['prabhu', 'deepak', 'abhijith', 'nandhu', 'vaibhav'], #zing
    '901606186300': ['prabhu', 'deepak', 'abhijith', 'nandhu', 'vaibhav'], #prathiksham
    '901606186304': ['prabhu', 'deepak', 'abhijith', 'nandhu', 'vaibhav'], #adoreaboo
    #video edit
    '901606178743': ['beelittle', 'prathiksham', 'zing', 'adoreaboo'], #prabhu
    '901606178750': ['beelittle', 'prathiksham', 'zing', 'adoreaboo'], #deepak
    '901606248381': ['beelittle', 'prathiksham', 'zing', 'adoreaboo'], #nandhu
    #graphic design
    '901606186292': ['beelittle', 'prathiksham', 'zing', 'adoreaboo'], #abhijtih
    '901606248361': ['beelittle', 'prathiksham', 'zing', 'adoreaboo'], #vaibhav
    #review
    '901606177816': ['all'], #beelittle
    '901606248338': ['all'], #prathiksham
    '901606248326': ['all'], #zing
    '901606248353': ['all'], #adoreaboo
}

def create_linked_tasks(list_ids, conditions):
    all_task_ids = []
    new_tasks_to_add = []
    tasks_by_list_id = {}
     
    for list_id in list_ids:
        print(f"Processing list ID: {list_id}")
        tasks = get_tasks(list_id, conditions)
        tasks_by_list_id[list_id] = tasks
        for task in tasks:
            task_id = task['id']
            all_task_ids.append(task_id)
            print(f"Processing task ID: {task_id} in list ID: {list_id}")

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
                        print(f"Task {task_id} already has linked tasks in the target list {linked_list_id}, skipping creation.")
                        continue

                    print(f"Creating linked task in list ID: {linked_list_id} for tag: {tag_name}")

                    # Fetch the available statuses for the target list
                    list_statuses = get_list_statuses(linked_list_id)
                    if list_statuses:
                        first_status = list_statuses[0]['status']
                    else:
                        first_status = 'to do'  # Fallback to 'to do' if no statuses are found
                    
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

                    response = create_task(linked_list_id, task['name'], task_details)
                    if 'err' in response:
                        print(f"Failed to create linked task for {task_id} in list {linked_list_id}: {response['err']}")
                    else:
                        linked_task_id = response['id']
                        new_linked_task_ids.add(linked_task_id)
                        print(f"Created linked task ID: {linked_task_id} for task ID: {task_id}")
                        link_response = link_tasks(task_id, linked_task_id)
                        if 'err' in link_response:
                            print(f"Failed to link task {task_id} with {linked_task_id}: {link_response['err']}")
                        else:
                            print(f"Successfully created and linked task {linked_task_id} for {task_id} in list {linked_list_id}")

                        # Add the new linked task to the list of tasks to add to the database
                        print(f"Adding linked task {linked_task_id} {task_id} {first_status} {linked_list_id} {','.join(tag['name'] for tag in task['tags'])}")
                        new_tasks_to_add.append((linked_task_id, task_id, first_status, linked_list_id, ",".join(tag['name'] for tag in task['tags'])))

    # Bulk add new linked tasks to the database
    if new_tasks_to_add:
        print(f"Adding {len(new_tasks_to_add)} new linked tasks to the database.")
        add_tasks_bulk(new_tasks_to_add)

    print(f"Processed {len(new_tasks_to_add)} new linked tasks.")
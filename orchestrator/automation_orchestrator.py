import logging
import json
from automation_rules.update_tasks_based_on_conditions import update_tasks_based_on_conditions
from automation_rules.create_linked_tasks import create_linked_tasks
from automation_rules.update_linked_tasks_backward import update_linked_tasks_backward
from automation_rules.update_linked_tasks_forward import update_linked_tasks_forward
from automation_rules.update_review_tasks_status import update_review_tasks_status
from automation_rules.update_main_tasks_status import update_main_tasks_status

# Configure logging for this script
logger = logging.getLogger('automation_orchestrator')
logger.setLevel(logging.INFO)
# Remove any existing handlers
if logger.hasHandlers():
    logger.handlers.clear()

file_handler = logging.FileHandler('logs/automation_orchestrator.log')
formatter = logging.Formatter('%(asctime)s %(levelname)s %(message)s')
file_handler.setFormatter(formatter)
logger.addHandler(file_handler)

# Disable propagation to avoid logging to the root logger
logger.propagate = False


# Load the configuration
with open('config/config.json', 'r') as config_file:
    config = json.load(config_file)

# Load the automation registry
with open('config/automation_registry.json', 'r') as registry_file:
    automation_registry = json.load(registry_file)

def get_list_ids(folders):
    list_ids = []
    for space in config['spaces']:
        for folder in space['folders']:
            if folder['folder_name'] in folders:
                for list in folder['lists']:
                    list_ids.append(list['list_id'])
    return list_ids

def execute_automation(automation):
    handler = automation['handler']
    conditions = automation['conditions']
    update_params = automation.get('update_params', {})

    #logger.info(f"Executing automation with handler: {handler}")

    if handler == 'automation_rules.update_tasks_based_on_conditions':
        logger.info("Starting update_tasks_based_on_conditions")
        folders = automation.get('folders', [])
        list_ids = get_list_ids(folders)
        update_tasks_based_on_conditions(list_ids, conditions, update_params)
        logger.info("Finished update_tasks_based_on_conditions")
    elif handler == 'automation_rules.create_linked_tasks':
        logger.info("Starting create_linked_tasks")
        folders = automation.get('folders', [])
        list_ids = get_list_ids(folders)
        create_linked_tasks(list_ids, conditions)
        logger.info("Finished create_linked_tasks")
    elif handler == 'automation_rules.update_linked_tasks_backward':
        logger.info("Starting update_linked_tasks_backward")
        folders = automation.get('folders', [])
        list_ids = get_list_ids(folders)
        update_linked_tasks_backward(list_ids, conditions, update_params)
        logger.info("Finished update_linked_tasks_backward")
    elif handler == 'automation_rules.update_linked_tasks_forward':
        logger.info("Starting update_linked_tasks_forward")
        folders = automation.get('folders', [])
        list_ids = get_list_ids(folders)
        update_linked_tasks_forward(list_ids, conditions, update_params)
        logger.info("Finished update_linked_tasks_forward")
    elif handler == 'automation_rules.update_review_tasks_status':
        logger.info("Starting update_review_tasks_status")
        folders = automation.get('folders', [])
        list_ids = get_list_ids(folders)
        update_review_tasks_status(list_ids, conditions, update_params)
        logger.info("Finished update_review_tasks_status")
    elif handler == 'automation_rules.update_main_tasks_status':
        logger.info("Starting update_main_tasks_status")
        folders = automation.get('folders', [])
        list_ids = get_list_ids(folders)
        update_main_tasks_status(list_ids, conditions, update_params)
        logger.info("Finished update_main_tasks_status")

def orchestrate_automations():
    #logger.info(f"Orchestrating automations: {automation_registry['automations']}")
    for automation in automation_registry['automations']:
        #logger.info(f"Orchestrating automation: {automation['name']}")
        execute_automation(automation)


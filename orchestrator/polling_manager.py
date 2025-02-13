import time
from datetime import datetime, timedelta
from polling.status_change import poll_for_status_changes
from polling.create_linked_tasks_polling import poll_for_linked_tasks_creation
from polling.update_linked_tasks import poll_for_update_linked_tasks
from polling.update_linked_tasks_forward import poll_for_update_linked_tasks_forward
from polling.update_review_tasks_status import poll_for_update_review_tasks_status
from polling.update_main_tasks_status import poll_for_update_main_tasks_status
# from polling.task_assignment import poll_for_task_assignments
# from polling.other_polling_script import poll_for_other_events

def poll_for_all_events(interval_minutes=2, duration_hours=1):
    end_time = datetime.now() + timedelta(hours=duration_hours)
    while datetime.now() < end_time:
        poll_for_status_changes(interval_minutes, duration_hours)
        poll_for_linked_tasks_creation(interval_minutes, duration_hours)
        poll_for_update_linked_tasks(interval_minutes, duration_hours)
        poll_for_update_linked_tasks_forward(interval_minutes, duration_hours)
        poll_for_update_review_tasks_status(interval_minutes, duration_hours)
        poll_for_update_main_tasks_status(interval_minutes, duration_hours)
        # poll_for_task_assignments(interval_minutes, duration_hours)
        # poll_for_other_events(interval_minutes, duration_hours)
        time.sleep(interval_minutes * 60)

# Example usage
if __name__ == "__main__":
    poll_for_all_events(interval_minutes=1, duration_hours=1)



""""
import time
from datetime import datetime, timedelta
import threading
from polling.status_change import poll_for_status_changes
from polling.create_linked_tasks_polling import poll_for_linked_tasks_creation
# from polling.task_assignment import poll_for_task_assignments
# from polling.other_polling_script import poll_for_other_events

# Create a lock to ensure only one polling function runs at a time
polling_lock = threading.Lock()

def poll_for_status_changes_wrapper(interval_minutes, duration_hours, next_start_time):
    end_time = datetime.now() + timedelta(hours=duration_hours)
    while datetime.now() < end_time:
        with polling_lock:
            poll_for_status_changes()
        next_start_time['status_changes'] = datetime.now() + timedelta(minutes=interval_minutes)
        time.sleep(max(0, (next_start_time['status_changes'] - datetime.now()).total_seconds()))

def poll_for_linked_tasks_creation_wrapper(interval_minutes, duration_hours, next_start_time):
    end_time = datetime.now() + timedelta(hours=duration_hours)
    while datetime.now() < end_time:
        with polling_lock:
            poll_for_linked_tasks_creation()
        next_start_time['linked_tasks'] = datetime.now() + timedelta(minutes=interval_minutes)
        time.sleep(max(0, (next_start_time['linked_tasks'] - datetime.now()).total_seconds()))

def poll_for_other_events_wrapper(interval_minutes, duration_hours, next_start_time):
    end_time = datetime.now() + timedelta(hours=duration_hours)
    while datetime.now() < end_time:
        with polling_lock:
            poll_for_other_events()
        next_start_time['other_events'] = datetime.now() + timedelta(minutes=interval_minutes)
        time.sleep(max(0, (next_start_time['other_events'] - datetime.now()).total_seconds()))

def poll_for_all_events(status_change_interval, linked_tasks_interval, other_events_interval, duration_hours=1):
    next_start_time = {
        'status_changes': datetime.now(),
        'linked_tasks': datetime.now(),
        'other_events': datetime.now()
    }

    status_change_thread = threading.Thread(target=poll_for_status_changes_wrapper, args=(status_change_interval, duration_hours, next_start_time))
    linked_tasks_thread = threading.Thread(target=poll_for_linked_tasks_creation_wrapper, args=(linked_tasks_interval, duration_hours, next_start_time))
    other_events_thread = threading.Thread(target=poll_for_other_events_wrapper, args=(other_events_interval, duration_hours, next_start_time))

    status_change_thread.start()
    linked_tasks_thread.start()
    other_events_thread.start()

    status_change_thread.join()
    linked_tasks_thread.join()
    other_events_thread.join()

# Example usage
if __name__ == "__main__":
    poll_for_all_events(status_change_interval=5, linked_tasks_interval=2, other_events_interval=20, duration_hours=1)
"""""
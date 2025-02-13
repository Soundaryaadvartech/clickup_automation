import time
from datetime import datetime, timedelta
from orchestrator.automation_orchestrator import orchestrate_automations

def poll_for_update_linked_tasks(interval_minutes=5, duration_hours=1):
    end_time = datetime.now() + timedelta(hours=duration_hours)
    while datetime.now() < end_time:
        orchestrate_automations()
        time.sleep(interval_minutes * 60)


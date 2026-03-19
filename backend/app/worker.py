from celery import Celery
import os

REDIS_URL = os.getenv("REDIS_URL", "redis://redis:6379/0")
celery_app = Celery("tasks", broker=REDIS_URL, backend=REDIS_URL)

@celery_app.task(name="execute_view_task")
def execute_view_task(target_url, duration):
    print(f"[WORKER] Starting view task for {target_url} ({duration}s)")
    # Selenium logic would go here
    return {"status": "success", "url": target_url}
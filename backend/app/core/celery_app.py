from celery import Celery
from app.core.config import settings

celery_app = Celery(
    "worker",
    broker=f"redis://{settings.REDIS_HOST}:6379/0",
    backend=f"redis://{settings.REDIS_HOST}:6379/0"
)

celery_app.conf.task_routes = {
    "app.tasks.mobile.*": "mobile-queue",
    "app.tasks.browser.*": "browser-queue",
}

celery_app.autodiscover_tasks(["app.tasks"])

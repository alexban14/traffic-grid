from celery import Celery
from app.core.config import settings

celery_app = Celery(
    "trafficgrid",
    broker=settings.REDIS_URL,
    backend=settings.REDIS_URL,
)

celery_app.conf.task_routes = {
    "app.tasks.mobile.*": {"queue": "mobile-queue"},
    "app.tasks.browser.*": {"queue": "browser-queue"},
}
celery_app.conf.task_track_started = True
celery_app.conf.result_extended = True

celery_app.autodiscover_tasks(["app.tasks"])

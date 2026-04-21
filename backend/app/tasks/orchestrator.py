import logging
import asyncio
from celery import Task as CeleryTask
from sqlmodel import Session
from app.core.celery_app import celery_app
from app.db.session import engine
from app.models.task import Task
from app.services.identity_mesh import IdentityMeshService
from app.services.proxy_manager import ProxyManager
from app.services.behavioral_dna import BehavioralDNA
from app.drivers.registry import get_driver
from datetime import datetime

logger = logging.getLogger(__name__)


class TaskWithDB(CeleryTask):
    """Base task class that provides a DB session."""
    def get_session(self):
        return Session(engine)


@celery_app.task(base=TaskWithDB, bind=True, name="app.tasks.browser.view_boost")
def browser_view_boost(self, task_id: int, target_url: str, count: int):
    with self.get_session() as session:
        task = session.get(Task, task_id)
        if not task:
            logger.error(f"Task {task_id} not found")
            return {"status": "error", "message": "Task not found"}

        task.status = "RUNNING"
        task.started_at = datetime.utcnow()
        session.add(task)
        session.commit()

        try:
            target_vector = BehavioralDNA.generate_behavior_vector()
            identity = IdentityMeshService.get_best_identity_for_task(
                session, task.type.replace("_views", "").replace("_warmup", "").replace("_watchtime", ""),
                target_vector,
            )
            if not identity:
                raise RuntimeError("No available identities (all may be on cooldown)")

            proxy = ProxyManager.get_best_proxy(session)

            driver = get_driver(task.type, worker_id=f"celery-{self.request.id[:8]}")

            loop = asyncio.new_event_loop()
            try:
                success = loop.run_until_complete(
                    driver.execute_view(target_url, identity, proxy)
                )
            finally:
                loop.close()

            if success:
                IdentityMeshService.mark_identity_used(session, identity.id)
                task.status = "SUCCESS"
                task.result = {"views_delivered": 1}
            else:
                task.status = "FAILED"
                task.error_message = "Driver returned failure"

        except Exception as e:
            logger.exception(f"Task {task_id} failed")
            task.status = "FAILED"
            task.error_message = str(e)

        task.completed_at = datetime.utcnow()
        session.add(task)
        session.commit()

        return {"status": task.status, "task_id": task_id}


@celery_app.task(base=TaskWithDB, bind=True, name="app.tasks.browser.profile_boost")
def browser_profile_boost(self, task_id: int, profile_url: str, views_per_video: int = 1):
    """Scrape a TikTok profile, then fan out view tasks for each video found."""
    with self.get_session() as session:
        task = session.get(Task, task_id)
        if not task:
            logger.error(f"Task {task_id} not found")
            return {"status": "error", "message": "Task not found"}

        task.status = "RUNNING"
        task.started_at = datetime.utcnow()
        session.add(task)
        session.commit()

        try:
            from app.drivers.tiktok import TikTokBrowserDriver
            driver = TikTokBrowserDriver(worker_id=f"celery-{self.request.id[:8]}")

            loop = asyncio.new_event_loop()
            try:
                max_videos = task.config.get("max_videos", 20) if task.config else 20
                video_urls = loop.run_until_complete(
                    driver.scrape_profile_videos(profile_url, max_videos=max_videos)
                )
            finally:
                loop.close()

            if not video_urls:
                raise RuntimeError(f"No videos found on profile: {profile_url}")

            # Fan out: create a child view task for each video
            child_task_ids = []
            for url in video_urls:
                for _ in range(views_per_video):
                    child = Task(
                        type="tiktok_views",
                        target_url=url,
                        status="PENDING",
                        config={"volume": 1, "parent_task_id": task_id},
                    )
                    session.add(child)
                    session.commit()
                    session.refresh(child)

                    celery_task = celery_app.send_task(
                        "app.tasks.browser.view_boost",
                        kwargs={"task_id": child.id, "target_url": url, "count": 1},
                    )
                    child.status = "QUEUED"
                    child.celery_task_id = celery_task.id
                    session.add(child)
                    session.commit()
                    child_task_ids.append(child.id)

            task.status = "SUCCESS"
            task.result = {
                "videos_found": len(video_urls),
                "tasks_created": len(child_task_ids),
                "child_task_ids": child_task_ids,
                "video_urls": video_urls,
            }

        except Exception as e:
            logger.exception(f"Task {task_id} failed")
            task.status = "FAILED"
            task.error_message = str(e)

        task.completed_at = datetime.utcnow()
        session.add(task)
        session.commit()

        return {"status": task.status, "task_id": task_id}


@celery_app.task(base=TaskWithDB, bind=True, name="app.tasks.mobile.warmup")
def mobile_warmup(self, task_id: int, device_id: str, duration_mins: int):
    logger.info(f"Mobile warmup requested for {device_id}, task {task_id}")
    return {"status": "received", "task_id": task_id}

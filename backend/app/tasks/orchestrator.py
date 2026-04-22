import logging
import asyncio
from typing import Optional
from celery import Task as CeleryTask
from sqlmodel import Session
from sqlalchemy import select, and_
from app.core.celery_app import celery_app
from app.db.session import engine
from app.models.task import Task
from app.models.identity import Identity
from app.services.identity_mesh import IdentityMeshService
from app.services.proxy_manager import ProxyManager
from app.services.behavioral_dna import BehavioralDNA
from app.drivers.registry import get_driver
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)

COOLDOWN_HOURS = 2


class TaskWithDB(CeleryTask):
    """Base task class that provides a DB session."""
    def get_session(self):
        return Session(engine)


def _get_available_identities(session: Session, platform: str) -> list[Identity]:
    """Fetch all active identities for a platform that are not on cooldown."""
    cooldown_cutoff = datetime.utcnow() - timedelta(hours=COOLDOWN_HOURS)
    statement = (
        select(Identity)
        .where(
            and_(
                Identity.platform == platform,
                Identity.status == "active",
                (Identity.last_used_at.is_(None)) | (Identity.last_used_at <= cooldown_cutoff),
            )
        )
        .order_by(Identity.last_used_at.asc().nulls_first())
    )
    rows = session.exec(statement).all()
    # Unwrap SQLAlchemy Row objects
    return [r[0] if not isinstance(r, Identity) else r for r in rows]


@celery_app.task(base=TaskWithDB, bind=True, name="app.tasks.browser.view_boost")
def browser_view_boost(self, task_id: int, target_url: str, count: int, identity_id: Optional[int] = None):
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
            # Use pre-assigned identity (round-robin) or fall back to reactive lookup
            if identity_id:
                identity = session.get(Identity, identity_id)
                if not identity:
                    raise RuntimeError(f"Pre-assigned identity {identity_id} not found")
            else:
                target_vector = BehavioralDNA.generate_behavior_vector()
                identity = IdentityMeshService.get_best_identity_for_task(
                    session,
                    task.type.replace("_views", "").replace("_warmup", "").replace("_watchtime", ""),
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
                task.result = {"views_delivered": 1, "identity_used": identity.username}
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
    """Scrape a TikTok profile, then fan out view tasks with round-robin identity assignment."""
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

            # Fetch available identities for round-robin assignment
            identities = _get_available_identities(session, "tiktok")
            if not identities:
                raise RuntimeError("No available TikTok identities (all on cooldown)")

            total_tasks_needed = len(video_urls) * views_per_video
            logger.info(
                f"Profile boost: {len(video_urls)} videos × {views_per_video} views = "
                f"{total_tasks_needed} tasks, {len(identities)} identities available"
            )

            # Fan out with round-robin identity assignment
            child_task_ids = []
            identity_idx = 0

            for url in video_urls:
                for _ in range(views_per_video):
                    assigned_identity = identities[identity_idx % len(identities)]
                    identity_idx += 1

                    child = Task(
                        type="tiktok_views",
                        target_url=url,
                        status="PENDING",
                        config={
                            "volume": 1,
                            "parent_task_id": task_id,
                            "identity_id": assigned_identity.id,
                            "identity_username": assigned_identity.username,
                        },
                    )
                    session.add(child)
                    session.commit()
                    session.refresh(child)

                    celery_task = celery_app.send_task(
                        "app.tasks.browser.view_boost",
                        kwargs={
                            "task_id": child.id,
                            "target_url": url,
                            "count": 1,
                            "identity_id": assigned_identity.id,
                        },
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
                "identities_used": min(len(identities), total_tasks_needed),
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


@celery_app.task(base=TaskWithDB, bind=True, name="app.tasks.browser.warmup")
def browser_warmup(self, task_id: int, identity_id: int, duration_mins: int = 3):
    """Warm up an identity by browsing TikTok FYP to build session cookies."""
    with self.get_session() as session:
        task = session.get(Task, task_id)
        if not task:
            return {"status": "error", "message": "Task not found"}

        identity = session.get(Identity, identity_id)
        if not identity:
            task.status = "FAILED"
            task.error_message = f"Identity {identity_id} not found"
            session.add(task)
            session.commit()
            return {"status": "error", "message": task.error_message}

        task.status = "RUNNING"
        task.started_at = datetime.utcnow()
        session.add(task)
        session.commit()

        try:
            from app.drivers.tiktok import TikTokBrowserDriver
            driver = TikTokBrowserDriver(worker_id=f"celery-{self.request.id[:8]}")

            loop = asyncio.new_event_loop()
            try:
                success = loop.run_until_complete(
                    driver.execute_warmup(identity, duration_mins=duration_mins)
                )
            finally:
                loop.close()

            if success:
                task.status = "SUCCESS"
                task.result = {"identity": identity.username, "duration_mins": duration_mins}
            else:
                task.status = "FAILED"
                task.error_message = "Warmup returned failure"

        except Exception as e:
            logger.exception(f"Warmup task {task_id} failed")
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

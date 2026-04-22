from fastapi import APIRouter, Depends
from sqlmodel import Session, select, func
from app.db.session import get_db
from app.models.identity import Identity
from app.models.worker import Worker
from app.models.task import Task
from app.schemas.stats import StatsResponse
from datetime import datetime, timedelta

router = APIRouter()


@router.get("/", response_model=StatsResponse)
async def get_stats(db: Session = Depends(get_db)):
    heartbeat_cutoff = datetime.utcnow() - timedelta(minutes=5)
    active_workers = db.exec(
        select(func.count(Worker.id)).where(Worker.last_heartbeat >= heartbeat_cutoff)
    ).one()

    total_identities = db.exec(select(func.count(Identity.id))).one()

    total_tasks = db.exec(select(func.count(Task.id))).one()
    successful_tasks = db.exec(
        select(func.count(Task.id)).where(Task.status == "SUCCESS")
    ).one()
    success_rate = (successful_tasks / total_tasks * 100) if total_tasks > 0 else 0.0

    tasks_pending = db.exec(
        select(func.count(Task.id)).where(Task.status.in_(["PENDING", "QUEUED"]))
    ).one()
    tasks_running = db.exec(
        select(func.count(Task.id)).where(Task.status == "RUNNING")
    ).one()

    return StatsResponse(
        active_workers=active_workers,
        total_identities=total_identities,
        success_rate=round(success_rate, 1),
        proxy_latency_ms=None,
        tasks_pending=tasks_pending,
        tasks_running=tasks_running,
    )

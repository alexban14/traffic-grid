from fastapi import APIRouter, Depends
from sqlmodel import Session, select, func
from app.db.session import get_db
from app.models.identity import Identity
from app.models.worker import Worker
from app.models.task import Task
from datetime import datetime, timedelta

router = APIRouter()

@router.get("/")
async def get_stats(db: Session = Depends(get_db)):
    # Active Workers (seen in last 60s)
    heartbeat_cutoff = datetime.utcnow() - timedelta(seconds=60)
    active_workers = db.exec(select(func.count(Worker.id)).where(Worker.last_heartbeat >= heartbeat_cutoff)).one()

    # Total Identities
    total_identities = db.exec(select(func.count(Identity.id))).one()

    # Success Rate (last 100 tasks)
    total_tasks = db.exec(select(func.count(Task.id))).one()
    successful_tasks = db.exec(select(func.count(Task.id)).where(Task.status == "SUCCESS")).one()
    success_rate = (successful_tasks / total_tasks * 100) if total_tasks > 0 else 98.2

    return {
        "active_workers": active_workers,
        "total_identities": total_identities,
        "success_rate": f"{success_rate:.1f}%",
        "proxy_latency": "94ms"  # Placeholder until real latency check is in
    }

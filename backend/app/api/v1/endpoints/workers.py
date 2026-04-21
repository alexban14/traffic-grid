from fastapi import APIRouter, Depends, WebSocket, WebSocketDisconnect
from sqlmodel import Session, select
from app.db.session import get_db
from app.models.worker import Worker
from app.models.task import Task
from app.schemas.task import DispatchRequest, DispatchResponse, TaskStatus
from app.schemas.worker import WorkerHeartbeatRequest, WorkerHeartbeatResponse, WorkerStatusResponse
from app.core.celery_app import celery_app
from app.core.websocket import manager
from datetime import datetime
from typing import List

router = APIRouter()


@router.post("/dispatch", response_model=DispatchResponse)
async def dispatch_task(body: DispatchRequest, db: Session = Depends(get_db)):
    task = Task(
        type=body.task_type.value,
        target_url=body.target_url,
        status=TaskStatus.PENDING.value,
        config={"volume": body.volume},
    )
    db.add(task)
    db.commit()
    db.refresh(task)

    if body.task_type.value == "tiktok_profile_boost":
        celery_task = celery_app.send_task(
            "app.tasks.browser.profile_boost",
            kwargs={
                "task_id": task.id,
                "profile_url": body.target_url,
                "views_per_video": body.volume,
            },
        )
    else:
        celery_task = celery_app.send_task(
            "app.tasks.browser.view_boost",
            kwargs={"task_id": task.id, "target_url": body.target_url, "count": body.volume},
        )

    task.status = TaskStatus.QUEUED.value
    task.celery_task_id = celery_task.id
    db.add(task)
    db.commit()

    return DispatchResponse(
        task_id=task.id,
        celery_task_id=celery_task.id,
        status=TaskStatus.QUEUED,
    )


@router.post("/heartbeat", response_model=WorkerHeartbeatResponse)
async def worker_heartbeat(body: WorkerHeartbeatRequest, db: Session = Depends(get_db)):
    statement = select(Worker).where(Worker.name == body.name)
    worker = db.exec(statement).first()

    if not worker:
        worker = Worker(name=body.name, type=body.type, ip_address=body.ip_address)

    worker.last_heartbeat = datetime.utcnow()
    worker.status = "IDLE"
    db.add(worker)
    db.commit()
    db.refresh(worker)
    return WorkerHeartbeatResponse(status="acknowledged", worker_id=worker.id)


@router.get("/status", response_model=List[WorkerStatusResponse])
async def get_workers_status(db: Session = Depends(get_db)):
    workers = db.exec(select(Worker)).all()
    return [
        WorkerStatusResponse(
            id=w.name,
            type="physical" if "S24" in w.type or "MOTO" in w.type else "lxc",
            status=w.status.lower(),
            load=0,
            last_seen=w.last_heartbeat,
        )
        for w in workers
    ]


@router.websocket("/{worker_id}/ws")
async def worker_websocket_endpoint(websocket: WebSocket, worker_id: str):
    await manager.connect(websocket, worker_id)
    try:
        while True:
            data = await websocket.receive_text()
            await manager.send_personal_message(f"ACK: {data}", websocket)
    except WebSocketDisconnect:
        manager.disconnect(websocket, worker_id)

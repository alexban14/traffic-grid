from fastapi import APIRouter, Depends, WebSocket, WebSocketDisconnect, HTTPException
from sqlmodel import Session, select
from app.db.session import get_db
from app.models.worker import Worker
from datetime import datetime
from typing import List
from app.core.websocket import manager

router = APIRouter()

@router.post("/heartbeat")
async def worker_heartbeat(name: str, type: str, ip_address: str, db: Session = Depends(get_db)):
    statement = select(Worker).where(Worker.name == name)
    worker = db.exec(statement).first()
    
    if not worker:
        worker = Worker(name=name, type=type, ip_address=ip_address)
    
    worker.last_heartbeat = datetime.utcnow()
    worker.status = "IDLE" # Reset to IDLE on heartbeat unless busy
    db.add(worker)
    db.commit()
    db.refresh(worker)
    return {"status": "acknowledged", "worker_id": worker.id}

@router.get("/status", response_model=List[dict])
async def get_workers_status(db: Session = Depends(get_db)):
    workers = db.exec(select(Worker)).all()
    return [
        {
            "id": w.name,
            "type": "physical" if "S24" in w.type or "MOTO" in w.type else "lxc",
            "status": w.status.lower(),
            "load": 0, # Load monitoring to be implemented
            "last_seen": w.last_heartbeat
        } for w in workers
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

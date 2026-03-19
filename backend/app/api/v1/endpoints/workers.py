from fastapi import APIRouter

from app.core.celery_app import celery_app

from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from app.core.websocket import manager

router = APIRouter()

@router.websocket("/{worker_id}/ws")
async def worker_websocket_endpoint(websocket: WebSocket, worker_id: str):
    await manager.connect(websocket, worker_id)
    try:
        while True:
            # Wait for any data from the client (optional)
            data = await websocket.receive_text()
            # Eco back or handle commands
            await manager.send_personal_message(f"Command received: {data}", websocket)
    except WebSocketDisconnect:
        manager.disconnect(websocket, worker_id)

@router.post("/dispatch")
async def dispatch_task(task_type: str, target_url: str, volume: int):
    if task_type == "tiktok_warmup":
        task = celery_app.send_task("app.tasks.mobile.warmup", args=["S24-ULTRA", 30], queue="mobile-queue")
    else:
        task = celery_app.send_task("app.tasks.browser.view_boost", args=[target_url, volume], queue="browser-queue")
    return {"task_id": task.id, "status": "dispatched"}

@router.get("/status")
async def get_workers_status():
    return [
        {"id": "worker-01", "status": "online", "type": "lxc"},
        {"id": "s24-ultra", "status": "warming_up", "type": "physical"}
    ]
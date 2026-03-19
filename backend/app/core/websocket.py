from typing import List, Dict
from fastapi import WebSocket

class ConnectionManager:
    def __init__(self):
        # Map of worker_id -> list of active websockets
        self.active_connections: Dict[str, List[WebSocket]] = {}

    async def connect(self, websocket: WebSocket, worker_id: str):
        await websocket.accept()
        if worker_id not in self.active_connections:
            self.active_connections[worker_id] = []
        self.active_connections[worker_id].append(websocket)

    def disconnect(self, websocket: WebSocket, worker_id: str):
        if worker_id in self.active_connections:
            self.active_connections[worker_id].remove(websocket)

    async def send_personal_message(self, message: str, websocket: WebSocket):
        await websocket.send_text(message)

    async def broadcast_to_worker(self, message: str, worker_id: str):
        if worker_id in self.active_connections:
            for connection in self.active_connections[worker_id]:
                await connection.send_text(message)

manager = ConnectionManager()
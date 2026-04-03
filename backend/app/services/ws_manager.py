from collections import defaultdict
from fastapi import WebSocket

class ConnectionManager:
    def __init__(self):
        self.active_connections: dict[int, list[WebSocket]] = defaultdict(list)

    async def connect(self, room_id: int, websocket: WebSocket):
        await websocket.accept()
        self.active_connections[room_id].append(websocket)

    def disconnect(self, room_id: int, websocket: WebSocket):
        connections = self.active_connections.get(room_id, [])
        if websocket in connections:
            connections.remove(websocket)
        if not connections and room_id in self.active_connections:
            del self.active_connections[room_id]

    async def send_personal_message(self, websocket: WebSocket, payload: dict):
        await websocket.send_json(payload)

    async def broadcast(self, room_id: int, payload: dict):
        connections = list(self.active_connections.get(room_id, []))
        dead_connections = []

        for connection in connections:
            try:
                await connection.send_json(payload)
            except Exception:
                dead_connections.append(connection)

        for dead in dead_connections:
            self.disconnect(room_id, dead)

    def room_connection_count(self, room_id: int) -> int:
        return len(self.active_connections.get(room_id, []))


manager = ConnectionManager()

import asyncio
from typing import List
from fastapi import WebSocket

class ConnectionManager:
    def __init__(self):
        self.active_connections: List[WebSocket] = []
        self._loop: asyncio.AbstractEventLoop | None = None

    def set_loop(self, loop: asyncio.AbstractEventLoop):
        self._loop = loop

    async def connect(self, ws: WebSocket):
        await ws.accept()
        self.active_connections.append(ws)

    def disconnect(self, ws: WebSocket):
        self.active_connections.remove(ws)

    async def broadcast(self, message: str):
        for ws in self.active_connections:
            await ws.send_text(message)

    def schedule_broadcast(self, message: str):
        if not self._loop:
            raise RuntimeError("Event loop não foi configurado")
        asyncio.run_coroutine_threadsafe(self.broadcast(message), self._loop)

manager = ConnectionManager()

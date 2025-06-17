from fastapi import APIRouter, WebSocket, WebSocketDisconnect
import asyncio
from app.websocket.manager import manager
import structlog

logger = structlog.get_logger()
router = APIRouter()

@router.websocket("/ws/alerts")
async def alerts_ws(websocket: WebSocket):
    await manager.connect(websocket)
    logger.info(event="ws_connect", action="connect")
    try:
        await asyncio.Event().wait()
    except WebSocketDisconnect:
        manager.disconnect(websocket)
        logger.info("ws_disconnect", event="disconnect")

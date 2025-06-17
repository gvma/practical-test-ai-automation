import asyncio
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from app.config.config import lifespan
from app.exceptions import handlers
from app.exceptions.exceptions import NotFoundException, UseCaseException, DBException
from app.controllers.ticket_controller import router as tickets_router
from app.websocket.manager import manager

app = FastAPI(lifespan=lifespan) # type: ignore

app.add_exception_handler(UseCaseException, handlers.use_case_exception_handler) # type: ignore
app.add_exception_handler(DBException, handlers.db_exception_handler) # type: ignore
app.add_exception_handler(NotFoundException, handlers.not_found_exception_handler) # type: ignore
app.add_exception_handler(Exception, handlers.generic_exception_handler)


@app.websocket("/ws/alerts")
async def alerts_ws(websocket: WebSocket):
    await manager.connect(websocket)
    try:
        await asyncio.Event().wait()
    except WebSocketDisconnect:
        manager.disconnect(websocket)

app.include_router(tickets_router)

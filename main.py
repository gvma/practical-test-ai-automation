from fastapi import FastAPI, Depends
from app.config.config import lifespan
from app.config.exception_handlers import register_exception_handlers
from app.config.logging import setup_logging
from app.controllers.ticket_controller import router as tickets_router
from app.websocket.routes import router as websocket_router
from app.dependencies import logging_dependency
import structlog

setup_logging()
logger = structlog.get_logger()

app = FastAPI(lifespan=lifespan)

register_exception_handlers(app)

app.include_router(
    tickets_router,
    dependencies=[Depends(logging_dependency)],
)

app.include_router(websocket_router)

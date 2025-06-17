from sqlmodel import SQLModel
from contextlib import asynccontextmanager
from fastapi import FastAPI
from apscheduler.schedulers.asyncio import AsyncIOScheduler # type: ignore

from app.config.sla_config import SLAConfig
from app.config.sla_config_watcher import start_config_watcher
from app.config.settings import settings
from app.db.db import engine
from app.services.ticket_service import TicketService

import logging

logging.basicConfig(level=logging.INFO)

scheduler = AsyncIOScheduler()

def schedule_jobs():
    scheduler.add_job( # type: ignore
        TicketService().escalate_workflow,
        trigger="interval",
        seconds=int(settings.SCHEDULER_SECONDS_INTERVAL),
        id="escalation_workflow",
        max_instances=1,
        coalesce=True,
    )

@asynccontextmanager
async def lifespan(app: FastAPI):
    SLAConfig.load_config()
    start_config_watcher()

    SQLModel.metadata.create_all(engine)

    from app.websocket.manager import manager
    import asyncio
    manager.set_loop(asyncio.get_event_loop())

    schedule_jobs()
    scheduler.start()

    yield

    scheduler.shutdown()
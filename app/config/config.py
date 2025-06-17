from sqlmodel import SQLModel
from dotenv import load_dotenv
from contextlib import asynccontextmanager
from fastapi import FastAPI
from apscheduler.schedulers.asyncio import AsyncIOScheduler # type: ignore
import os
import logging

from app.config.sla_config import SLAConfig
from app.config.sla_config_watcher import start_config_watcher
from app.db.db import engine
from app.services.ticket_service import TicketService

load_dotenv()
logging.basicConfig(level=logging.INFO)

scheduler_seconds_interval = os.getenv("SCHEDULER_SECONDS_INTERVAL")
if scheduler_seconds_interval is None:
    raise RuntimeError("Scheduler seconds interval is not set.")

# Using AsyncIOScheduler to run jobs in the same event loop as FastAPI/Uvicorn
scheduler = AsyncIOScheduler()

def schedule_jobs():
    scheduler.add_job( # type: ignore
        TicketService().escalate_workflow,
        trigger="interval",
        seconds=int(scheduler_seconds_interval), # type: ignore
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
    print("Scheduler finalizado")
from contextvars import ContextVar
import logging
import structlog
import sys
from typing import Optional, Any
from structlog.types import EventDict

correlation_id_ctx: ContextVar[str] = ContextVar(
    "correlation_id",
    default="",
)
ticket_id_ctx: ContextVar[Optional[int]] = ContextVar(
    "ticket_id",
    default=None,
)

def add_contextvars(
    logger: Any,
    method_name: str,
    event_dict: EventDict,
) -> EventDict:
    event_dict["correlation_id"] = correlation_id_ctx.get()
    event_dict["ticket_id"] = ticket_id_ctx.get()
    return event_dict


def setup_logging() -> None:
    logging.basicConfig(
        format="%(message)s",
        stream=sys.stdout,
        level=logging.INFO,
    )
    structlog.configure(
        processors=[
            structlog.contextvars.merge_contextvars,  # inject contextvars
            add_contextvars,                          # custom processor
            structlog.processors.TimeStamper(fmt="iso"),
            structlog.processors.JSONRenderer(),      # emit JSON
        ],
        context_class=dict,
        logger_factory=structlog.stdlib.LoggerFactory(),
        wrapper_class=structlog.stdlib.BoundLogger,
        cache_logger_on_first_use=True,
    )

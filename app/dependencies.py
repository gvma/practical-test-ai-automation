from fastapi import Request
from typing import AsyncGenerator, Optional
from time import perf_counter
from uuid import uuid4
import structlog

from app.config.logging import correlation_id_ctx, ticket_id_ctx

async def logging_dependency(request: Request) -> AsyncGenerator[None, None]:
    corr = request.headers.get("X-Correlation-ID", str(uuid4()))
    correlation_id_ctx.set(corr)

    start = perf_counter()

    yield

    latency = perf_counter() - start

    raw_tid: Optional[str] = request.path_params.get("ticket_id")
    if raw_tid is not None:
        ticket_id_ctx.set(int(raw_tid))

    structlog.get_logger().info(
        "request_completed",
        method    = request.method,
        path      = request.url.path,
        operation = "http_request",
        latency   = latency,
    )

    ticket_id_ctx.set(None)

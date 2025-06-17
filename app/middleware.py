from fastapi.routing import APIRoute
from starlette.requests import Request
from starlette.responses import Response
from time import perf_counter
from uuid import uuid4
import structlog

from app.config.logging import correlation_id_ctx, ticket_id_ctx

class LoggingRoute(APIRoute):
    def get_route_handler(self):
        original = super().get_route_handler()
        
        async def custom(request: Request) -> Response:
            corr = request.headers.get("X-Correlation-ID", str(uuid4()))
            correlation_id_ctx.set(corr)

            start = perf_counter()
            response = await original(request)
            latency = perf_counter() - start

            tid = request.path_params.get("ticket_id")
            if tid is not None:
                ticket_id_ctx.set(int(tid))

            structlog.get_logger().info(
                "request_completed",
                method    = request.method,
                path      = request.url.path,
                operation = "http_request",
                latency   = latency,
            )

            ticket_id_ctx.set(None)
            return response

        return custom

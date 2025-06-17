from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from app.exceptions import handlers
from app.exceptions.exceptions import NotFoundException, UseCaseException, DBException


def register_exception_handlers(app: FastAPI) -> None:
    @app.exception_handler(UseCaseException)
    async def _use_case_exception_handler( # type: ignore
        request: Request, exc: UseCaseException
    ) -> JSONResponse:
        return await handlers.use_case_exception_handler(request, exc)

    @app.exception_handler(DBException)
    async def _db_exception_handler( # type: ignore
        request: Request, exc: DBException
    ) -> JSONResponse:
        return await handlers.db_exception_handler(request, exc)

    @app.exception_handler(NotFoundException)
    async def _not_found_exception_handler( # type: ignore
        request: Request, exc: NotFoundException
    ) -> JSONResponse:
        return await handlers.not_found_exception_handler(request, exc)

    @app.exception_handler(Exception)
    async def _generic_exception_handler( # type: ignore
        request: Request, exc: Exception
    ) -> JSONResponse:
        return await handlers.generic_exception_handler(request, exc)

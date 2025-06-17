from asyncio.log import logger
from fastapi import Request
from fastapi.responses import JSONResponse
from app.exceptions.exceptions import NotFoundException, UseCaseException, DBException

async def use_case_exception_handler(request: Request, exc: UseCaseException):
    logger.exception(f"UseCaseException on {request.url.path}: {exc}")
    return JSONResponse(
        status_code=400,
        content={
            "error": {
                "type": "UseCaseException",
                "message": str(exc),
                "path": request.url.path
            }
        }
    )

async def db_exception_handler(request: Request, exc: DBException):
    logger.exception(f"DBException on {request.url.path}: {exc}")
    return JSONResponse(
        status_code=400,
        content={
            "error": {
                "type": "DBException",
                "message": str(exc),
                "path": request.url.path
            }
        }
    )

async def generic_exception_handler(request: Request, exc: Exception):
    logger.exception(f"Unhandled exception on {request.url.path}: {exc}")
    return JSONResponse(
        status_code=500,
        content={
            "error": {
                "type": "InternalServerError",
                "message": "Erro interno do servidor",
                "path": request.url.path
            }
        }
    )
    
async def not_found_exception_handler(request: Request, exc: NotFoundException):
    logger.exception(f"NotFoundException on {request.url.path}: {exc}")
    return JSONResponse(
        status_code=404,
        content={
            "error": {
                "type": "NotFoundException",
                "message": str(exc),
                "path": request.url.path
            }
        }
    )


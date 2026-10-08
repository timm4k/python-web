from fastapi import HTTPException, Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse


class LinkNotFoundError(HTTPException):
    def __init__(self, short_code: str) -> None:
        self.short_code = short_code
        super().__init__(
            status.HTTP_404_NOT_FOUND, f"Link with code '{short_code}' was not found"
        )


async def link_not_found_handler(request: Request, error: Exception) -> JSONResponse:
    if not isinstance(error, LinkNotFoundError):
        raise error
    return JSONResponse(
        status_code=error.status_code,
        content={"error": "LINK_NOT_FOUND", "message": error.detail},
    )


async def validation_error_handler(request: Request, error: Exception) -> JSONResponse:
    if not isinstance(error, RequestValidationError):
        raise error
    errors: dict[str, str] = {}
    for item in error.errors():
        location = item["loc"]
        field_name = str(location[-1]) if location else "request"
        errors[field_name] = str(item["msg"])
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
        content={"errors": errors},
    )

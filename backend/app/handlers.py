from app.routes.app import app
from fastapi import Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse


@app.exception_handler(RequestValidationError)
def RequestValidationError_handler(request: Request, exc: RequestValidationError):
    errors = exc.errors()
    details = [
        {"loc": f"{'.'.join(str(loc) for loc in error['loc'])}", "msg": error["msg"]}
        for error in errors
    ]
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
        content={"message": "Переданы некорректные данные", "details": details},
    )

from datetime import datetime
from os import environ
from traceback import print_exception

from fastapi import FastAPI, HTTPException, Request
from fastapi.staticfiles import StaticFiles
from starlette.middleware.sessions import SessionMiddleware
from starlette.responses import HTMLResponse, RedirectResponse, Response
from starlette.status import (HTTP_429_TOO_MANY_REQUESTS, HTTP_401_UNAUTHORIZED,
                              HTTP_404_NOT_FOUND, HTTP_405_METHOD_NOT_ALLOWED,
                              HTTP_500_INTERNAL_SERVER_ERROR)
from slowapi.errors import RateLimitExceeded
from slowapi.middleware import SlowAPIMiddleware

import static
from app.config import SERVER_EXCEPTIONS_CODES
from app.routes import auth, env, panel
from app.dependencies import limiter

routers = (panel.router, auth.router)
app = FastAPI()
app.mount(
    "/static",
    StaticFiles(directory=static.__path__[0]),
    name="static",
)
app.state.limiter = limiter
app.add_middleware(SlowAPIMiddleware)
app.add_middleware(SessionMiddleware, secret_key=environ["SECRET_KEY"])

for router in routers:
    app.include_router(router)


@app.exception_handler(RateLimitExceeded)
async def rate_limit_handler(_request: Request, _exc: RateLimitExceeded) -> Response:
    return Response(status_code=HTTP_429_TOO_MANY_REQUESTS,
                    content="Слишком много неудачных попыток. Попробуйте позже")


@app.exception_handler(HTTP_401_UNAUTHORIZED)
def unauthorized_exception_handler(_request: Request, exc: HTTPException) -> RedirectResponse:
    return RedirectResponse(f"/?alert={exc.detail}")


@app.exception_handler(HTTP_404_NOT_FOUND)
@app.exception_handler(HTTP_405_METHOD_NOT_ALLOWED)
def not_found_exception_handler(_request: Request, _exc: HTTPException) -> HTMLResponse:
    template = env.get_template("404_not_found.html")
    page = template.render()
    return HTMLResponse(page)


def server_exception_handler(_request: Request, exc: ValueError) -> HTMLResponse:
    status_code = exc.status_code if hasattr(exc, "status_code") else HTTP_500_INTERNAL_SERVER_ERROR
    if hasattr(exc, "detail"):
        detail = exc.detail
    else:
        detail = exc.args[0] if len(exc.args) >= 1 else "No detail"

    template = env.get_template("500_internal_server_error.html")
    page = template.render(timestamp=datetime.now().strftime("%d.%m.%Y %H:%M:%S"),
                           status_code=status_code, detail=detail)
    print_exception(type(exc), exc, exc.__traceback__)
    return HTMLResponse(page)


for i in SERVER_EXCEPTIONS_CODES:
    app.add_exception_handler(i, server_exception_handler)

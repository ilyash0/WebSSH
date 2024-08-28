from datetime import datetime
from os import environ
from traceback import print_exception

from fastapi import FastAPI, Request, HTTPException
from fastapi.staticfiles import StaticFiles
from starlette.middleware.sessions import SessionMiddleware
from starlette.responses import RedirectResponse, HTMLResponse

import static
from app.config import SERVER_EXCEPTIONS_CODES
from app.routes import panel, auth, env

routers = (panel.router, auth.router)
app = FastAPI()
app.mount(
    "/static",
    StaticFiles(directory=static.__path__[0]),
    name="static",
)
app.add_middleware(SessionMiddleware, secret_key=environ["SECRET_KEY"])

for router in routers:
    app.include_router(router)


@app.exception_handler(401)
def unauthorized_exception_handler(_request: Request, exc: HTTPException) -> RedirectResponse:
    return RedirectResponse(f"/?alert={exc.detail}")


@app.exception_handler(404)
def not_found_exception_handler(_request: Request, _exc: HTTPException) -> HTMLResponse:
    template = env.get_template("404_not_found.html")
    page = template.render()
    return HTMLResponse(page)


def server_exception_handler(_request: Request, exc: ValueError) -> HTMLResponse:
    status_code = exc.status_code if hasattr(exc, "status_code") else 500
    detail = exc.detail if hasattr(exc, "detail") else exc.args[0] if len(exc.args) >= 1 else "No detail"
    template = env.get_template("500_internal_server_error.html")
    page = template.render(timestamp=datetime.now().strftime("%d.%m.%Y %H:%M:%S"), status_code=status_code,
                           detail=detail)
    print_exception(type(exc), exc, exc.__traceback__)
    return HTMLResponse(page)


for i in SERVER_EXCEPTIONS_CODES:
    app.add_exception_handler(i, server_exception_handler)

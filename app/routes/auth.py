from os import environ

from fastapi import APIRouter, Form, Request, Response
from traceback import print_exception
from starlette.responses import RedirectResponse, HTMLResponse
from starlette.status import HTTP_204_NO_CONTENT, HTTP_400_BAD_REQUEST, HTTP_200_OK, HTTP_500_INTERNAL_SERVER_ERROR

from . import env
from ..dependencies import connections, is_connected, disconnect_session

router = APIRouter(tags=["Authentication"])


@router.get("/")
def index_page(alert_type: str = "warning", alert: str = "", request: Request = Request):
    template = env.get_template("index.html")
    user_agent = request.headers.get("user-agent")
    if not alert and is_connected(user_agent):
        alert = "У вас уже есть текущее соединение"
        alert_type = "info"
    page = template.render(alert_type=alert_type, alert=alert)
    return HTMLResponse(page)


@router.post("/login/")
def login(username: str = Form(...), password: str = Form(...), request: Request = Request):
    user_agent = request.headers.get("user-agent")
    if is_connected(user_agent):
        disconnect_session(user_agent, request)

    try:
        if str(password) != str(environ["PASSWORD"]) or str(username) != str(environ["USERNAME"]):
            return Response(status_code=HTTP_400_BAD_REQUEST, content="Неверное имя пользователя или пароль")

        request.session["password"] = password
        connections.append(user_agent)
        return Response(status_code=HTTP_204_NO_CONTENT)
    except Exception as e:
        print_exception(type(e), e, e.__traceback__)
        return Response(status_code=HTTP_500_INTERNAL_SERVER_ERROR, content=e.__str__())


@router.get("/logout/")
def logout(request: Request = Request):
    user_agent = request.headers.get("user-agent")
    try:
        if is_connected(user_agent):
            disconnect_session(user_agent, request)

        return RedirectResponse(url="/")
    except Exception as e:
        print_exception(type(e), e, e.__traceback__)
        return Response(status_code=HTTP_500_INTERNAL_SERVER_ERROR, content=e.__str__())


@router.get("/status/")
def check_connection_status(request: Request = Request):
    user_agent = request.headers.get("user-agent")
    if not is_connected(user_agent):
        return Response(status_code=HTTP_200_OK, content="disconnected")
    return Response(status_code=HTTP_200_OK, content="connected")

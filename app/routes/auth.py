from asyncio import sleep
from datetime import datetime, timedelta
from os import environ

from fastapi import APIRouter, Form, Request, Response, BackgroundTasks
from traceback import print_exception
from starlette.responses import RedirectResponse, HTMLResponse
from starlette.status import HTTP_204_NO_CONTENT, HTTP_400_BAD_REQUEST, HTTP_500_INTERNAL_SERVER_ERROR

from . import env
from ..config import enable_idle_disconnect, time_to_disconnect
from ..dependencies import connections, is_connected, get_connection_or_none

router = APIRouter(tags=["Authentication"])


def disconnect_session(user_agent: str):
    connections.remove(get_connection_or_none(user_agent))


async def idle_disconnect(user_agent: str):
    await sleep(time_to_disconnect)
    if not is_connected(user_agent):
        return

    connection = get_connection_or_none(user_agent)
    if connection["login_time"] + timedelta(seconds=time_to_disconnect) < datetime.now():
        disconnect_session(user_agent)


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
def login(background_tasks: BackgroundTasks, username: str = Form(...), password: str = Form(...),
          request: Request = Request):
    user_agent = request.headers.get("user-agent")
    if is_connected(user_agent):
        disconnect_session(user_agent)

    try:
        if str(password) != str(environ["PASSWORD"]) or str(username) != str(environ["USERNAME"]):
            return Response(status_code=HTTP_400_BAD_REQUEST, content="Неверное имя пользователя или пароль")

        connections.append({"user_agent": user_agent, "login_time": datetime.now()})

        if enable_idle_disconnect:
            background_tasks.add_task(idle_disconnect, user_agent)
        return Response(status_code=HTTP_204_NO_CONTENT)
    except Exception as e:
        print_exception(type(e), e, e.__traceback__)
        return Response(status_code=HTTP_500_INTERNAL_SERVER_ERROR, content=e.__str__())


@router.get("/logout/")
def logout(request: Request = Request):
    user_agent = request.headers.get("user-agent")
    try:
        if is_connected(user_agent):
            disconnect_session(user_agent)

        return RedirectResponse(url="/")
    except Exception as e:
        print_exception(type(e), e, e.__traceback__)
        return Response(status_code=HTTP_500_INTERNAL_SERVER_ERROR, content=e.__str__())

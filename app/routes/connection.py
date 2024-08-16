from os import environ

from fastapi import APIRouter, Form, Request, Response
from traceback import print_exception
from starlette.responses import RedirectResponse

from ..dependencies import connections, is_connected, disconnect_session

router = APIRouter()


@router.post("/connect/")
def connect_to_remote(username: str = Form(...), password: str = Form(...), request: Request = Request):
    user_agent = request.headers.get("user-agent")
    if is_connected(user_agent):
        disconnect_session(user_agent, request)

    try:
        if str(password) != str(environ["PASSWORD"]) or str(username) != str(environ["USERNAME"]):
            return Response(status_code=400, content="Неверное имя пользователя или пароль")

        request.session["password"] = password
        connections.append(user_agent)
        return Response(status_code=204)
    except Exception as e:
        print_exception(type(e), e, e.__traceback__)
        return Response(status_code=500, content=e.__str__())


@router.get("/disconnect/")
def disconnect(alert: str = "", request: Request = Request):
    user_agent = request.headers.get("user-agent")
    try:
        if is_connected(user_agent):
            disconnect_session(user_agent, request)

        if alert:
            return RedirectResponse(url=f"/?alert={alert}")
        return RedirectResponse(url=f"/")
    except Exception as e:
        print_exception(type(e), e, e.__traceback__)
        return Response(status_code=500, content=e.__str__())


@router.get("/status/")
def status(request: Request = Request):
    user_agent = request.headers.get("user-agent")
    if not is_connected(user_agent):
        return Response(status_code=200, content="disconnected")
    return Response(status_code=200, content="connected")

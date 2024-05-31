from _socket import gaierror
from fastapi import APIRouter, Form, Request, Response
from paramiko import SSHClient, AutoAddPolicy
from traceback import print_exception

from paramiko.ssh_exception import AuthenticationException
from starlette.responses import RedirectResponse

from ..dependencies import connections, is_connected, disconnect_ssh

router = APIRouter()


@router.post("/connect/")
def connect_to_remote(host: str = Form(...), username: str = Form(...), password: str = Form(...),
                      request: Request = Request):
    user_agent = request.headers.get("user-agent")
    if is_connected(user_agent):
        disconnect_ssh(user_agent, request)

    try:
        if ":" in host:
            hostname, port = host.split(":")
        else:
            hostname = host
            port = 22

        hostname = "localhost" if hostname == "0.0.0.0" else hostname
        request.session["password"] = password
        request.session["username"] = username
        request.session["hostname"] = hostname

        ssh = SSHClient()
        ssh.set_missing_host_key_policy(AutoAddPolicy())
        ssh.connect(hostname, username=username, password=password, port=int(port))
        connections[user_agent] = ssh
        return Response(status_code=204)
    except gaierror as e:
        print_exception(type(e), e, e.__traceback__)
        return Response(status_code=400, content="Неверный адрес")
    except AuthenticationException as e:
        print_exception(type(e), e, e.__traceback__)
        return Response(status_code=400, content="Неверный логин или пароль")
    except Exception as e:
        print_exception(type(e), e, e.__traceback__)
        return Response(status_code=500, content=e.__str__())


@router.get("/disconnect/")
def disconnect(alert: str = "", request: Request = Request):
    user_agent = request.headers.get("user-agent")
    try:
        if is_connected(user_agent):
            disconnect_ssh(user_agent, request)

        if alert:
            return RedirectResponse(url=f"/?alert={alert}")
        return RedirectResponse(url=f"/")
    except Exception as e:
        print_exception(type(e), e, e.__traceback__)
        return Response(status_code=500, content=e.__str__())


@router.get("/status/")
def status(request: Request = Request):
    user_agent = request.headers.get("user-agent")
    if not connections.get(user_agent):
        request.session.pop("password")
        request.session.pop("username")
        request.session.pop("hostname")
        return Response(status_code=200, content="disconnected")
    elif not connections[user_agent].get_transport().active:
        connections.pop(user_agent)
        request.session.pop("password")
        request.session.pop("username")
        request.session.pop("hostname")
        return Response(status_code=200, content="disconnected")
    return Response(status_code=200, content="connected")

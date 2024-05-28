from fastapi import APIRouter, Form, Request, HTTPException, Response
from paramiko import SSHClient, AutoAddPolicy
from traceback import print_exception

from starlette.responses import RedirectResponse

from ..dependencies import connections

router = APIRouter()


@router.post("/connect/")
def connect_to_remote(host: str = Form(...), username: str = Form(...), password: str = Form(...),
                      request: Request = Request):
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
        connections[request.headers.get("user-agent")] = ssh
        return Response(status_code=200)
    except Exception as e:
        print_exception(type(e), e, e.__traceback__)
        raise HTTPException(status_code=400, detail=e.__str__())


@router.get("/disconnect/")
def disconnect(alert: str = "", request: Request = Request):
    user_agent = request.headers.get("user-agent")
    try:
        if not connections.get(user_agent):
            return RedirectResponse(url=f"/?alert={alert}")

        ssh = connections[user_agent]
        ssh.close()
        connections.pop(user_agent)
        request.session.pop("password")
        request.session.pop("username")
        request.session.pop("hostname")
        return RedirectResponse(url=f"/?alert={alert}")
    except Exception as e:
        print_exception(type(e), e, e.__traceback__)
        return HTTPException(status_code=400, detail=e.__str__())


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

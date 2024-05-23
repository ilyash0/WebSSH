from fastapi import APIRouter, Form, Request, HTTPException, Response
from paramiko import SSHClient, AutoAddPolicy
from traceback import print_exception

from starlette.responses import RedirectResponse

from ..dependencies import connections
from fastapi.templating import Jinja2Templates

templates = Jinja2Templates(directory="templates/")
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
def disconnect(request: Request = Request):
    try:
        ssh = connections[request.headers.get("user-agent")]
        ssh.close()
        connections.pop(request.headers.get("user-agent"))
        request.session.pop("password")
        return RedirectResponse(url="/")
    except Exception as e:
        print_exception(type(e), e, e.__traceback__)
        return HTTPException(status_code=400, detail=e.__str__())

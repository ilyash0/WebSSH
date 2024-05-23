from fastapi import APIRouter, Request
from starlette.responses import RedirectResponse
from traceback import print_exception

from ..dependencies import connections
from fastapi.templating import Jinja2Templates

templates = Jinja2Templates(directory="templates/")
router = APIRouter()


@router.get("/panel/")
def panel(request: Request = Request):
    if connections.get(request.headers.get("user-agent")) is None:
        return RedirectResponse("/?result=Нет+активного+соединения")

    return templates.TemplateResponse("panel.html", {"request": request, "hostname": request.session["hostname"],
                                                     "username": request.session["username"]})


@router.post("/reboot/")
def reboot_remote(request: Request = Request):
    try:
        ssh = connections[request.headers.get("user-agent")]
        ssh.exec_command(f"echo \"{request.session['password']}\" | sudo -S reboot")
        ssh.exec_command("sudo reboot")
        return templates.TemplateResponse("panel.html",
                                          {"request": request, "success": "Машина перезагружена. Соединения прервано",
                                           "hostname": request.session["hostname"],
                                           "username": request.session["username"]})
    except Exception as e:
        print_exception(type(e), e, e.__traceback__)
        return templates.TemplateResponse("panel.html", {"request": request, "danger": f"Ошибка: {e}",
                                                         "hostname": request.session["hostname"],
                                                         "username": request.session["username"]})


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
        return templates.TemplateResponse("panel.html", {"request": request, "danger": f"Ошибка: {e}",
                                                         "hostname": request.session["hostname"],
                                                         "username": request.session["username"]})

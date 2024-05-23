from fastapi import APIRouter, Request, UploadFile, File
from typing import List
from shutil import copyfileobj
from os import remove
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


@router.post("/upload/")
async def upload_file(files_list: List[UploadFile] = File(...), request: Request = Request):
    if not files_list:
        raise templates.TemplateResponse("panel.html", {"request": request, "danger": "Ошибка: отсутствует файл",
                                                        "hostname": request.session["hostname"],
                                                        "username": request.session["username"]})

    try:
        ssh = connections[request.headers.get("user-agent")]
        if not ssh:
            raise templates.TemplateResponse("panel.html", {"request": request,
                                                            "danger": "Ошибка: Не удалось подключиться к компьютеру",
                                                            "hostname": request.session["hostname"],
                                                            "username": request.session["username"]})

        sftp_client = ssh.open_sftp()
        for file in files_list:
            # Create a temporary file to save the downloaded file
            with open(file.filename, "wb") as buffer:
                copyfileobj(file.file, buffer)
            sftp_client.put(file.filename, f"/home/{request.session['username']}/{file.filename}")
            remove(file.filename)

        sftp_client.close()
        return templates.TemplateResponse("panel.html",
                                          {"request": request, "success": f"{len(files_list)} файла успешно переданы",
                                           "hostname": request.session["hostname"],
                                           "username": request.session["username"]})
    except Exception as e:
        print_exception(type(e), e, e.__traceback__)
        return templates.TemplateResponse("panel.html", {"request": request, "danger": f"Ошибка: {e}",
                                                         "hostname": request.session["hostname"],
                                                         "username": request.session["username"]})

from fastapi import APIRouter, Request, UploadFile, File, Response, HTTPException
from fastapi.responses import HTMLResponse
from typing import List
from shutil import copyfileobj
from os import remove
from starlette.responses import RedirectResponse
from traceback import print_exception

from . import env
from ..dependencies import connections

router = APIRouter()


@router.get("/panel/")
def panel(request: Request = Request):
    user_agent = request.headers.get("user-agent")
    if connections.get(user_agent) is None or not connections[user_agent].get_transport().active:
        return RedirectResponse("/disconnect/?alert=Нет+активного+соединения")

    return HTMLResponse(env.get_template("panel.html").render())


@router.post("/reboot/")
def reboot_remote(request: Request = Request):
    try:
        ssh = connections[request.headers.get("user-agent")]
        ssh.exec_command(f"echo \"{request.session['password']}\" | sudo -S reboot")
        return Response(status_code=200)
    except Exception as e:
        print_exception(type(e), e, e.__traceback__)
        return HTTPException(status_code=400, detail=e.__str__())


@router.post("/upload/")
async def upload_file(files_list: List[UploadFile] = File(...), request: Request = Request):
    if not files_list:
        raise HTTPException(status_code=400, detail="Отсутствует файл")

    try:
        ssh = connections[request.headers.get("user-agent")]
        if not ssh:
            raise HTTPException(status_code=400, detail="Не удалось подключиться к компьютеру")

        sftp_client = ssh.open_sftp()
        for file in files_list:
            # Create a temporary file to save the downloaded file
            with open(file.filename, "wb") as buffer:
                copyfileobj(file.file, buffer)
            sftp_client.put(file.filename, f"/home/{request.session['username']}/{file.filename}")
            remove(file.filename)

        sftp_client.close()
        return Response(status_code=200, content=f"{len(files_list)} файла успешно переданы")
    except Exception as e:
        print_exception(type(e), e, e.__traceback__)
        return HTTPException(status_code=400, detail=e.__str__())

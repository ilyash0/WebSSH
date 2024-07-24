from fastapi import APIRouter, Request, UploadFile, File, Response
from fastapi.responses import HTMLResponse
from typing import List
from shutil import copyfileobj
from os import system, path
from starlette.responses import RedirectResponse
from traceback import print_exception

from . import env
from ..dependencies import is_connected, upload_dir

router = APIRouter()


@router.get("/panel/")
def panel(request: Request = Request):
    user_agent = request.headers.get("user-agent")
    if not is_connected(user_agent):
        return RedirectResponse("/?alert=Нет+активного+соединения")

    template = env.get_template("panel.html")
    page = template.render(hostname=request.session["hostname"], username=request.session["username"])
    return HTMLResponse(page)


@router.post("/reboot/")
def reboot_remote(request: Request = Request):
    try:
        system(f"echo \"{request.session['password']}\" | sudo -S reboot")
        return Response(status_code=204)
    except Exception as e:
        print_exception(type(e), e, e.__traceback__)
        return Response(status_code=500, content=e.__str__())


@router.post("/upload/")
async def upload_file(files_list: List[UploadFile] = File(...)):
    if not files_list:
        return Response(status_code=400, content="Отсутствует файл")

    try:
        for file in files_list:
            file_path = path.join(upload_dir, file.filename)
            with open(file_path, "wb") as buffer:
                copyfileobj(file.file, buffer)

        return Response(status_code=200, content=f"{len(files_list)} файла успешно переданы")
    except PermissionError as e:
        print_exception(type(e), e, e.__traceback__)
        return Response(status_code=400, content="Не достаточно прав")
    except Exception as e:
        print_exception(type(e), e, e.__traceback__)
        return Response(status_code=500, content=e.__str__())

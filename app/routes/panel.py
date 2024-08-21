from fastapi import APIRouter, Request, UploadFile, File, Response
from typing import List
from shutil import copyfileobj
from os import system, path
from starlette.responses import HTMLResponse, RedirectResponse
from traceback import print_exception

from starlette.status import HTTP_204_NO_CONTENT, HTTP_403_FORBIDDEN, HTTP_400_BAD_REQUEST, HTTP_200_OK, \
    HTTP_500_INTERNAL_SERVER_ERROR

from . import env
from ..dependencies import is_connected
from ..config import upload_dir

router = APIRouter(prefix="/panel", tags=["Home app"])


@router.get("/")
def panel_page(request: Request = Request):
    user_agent = request.headers.get("user-agent")
    if not is_connected(user_agent):
        return RedirectResponse("/?alert=Нет+активного+соединения")

    template = env.get_template("panel.html")
    page = template.render()
    return HTMLResponse(page)


@router.post("/reboot/")
def reboot_remote_device(request: Request = Request):
    try:
        system(f"echo \"{request.session['password']}\" | sudo -S reboot")
        return Response(status_code=HTTP_204_NO_CONTENT)
    except Exception as e:
        print_exception(type(e), e, e.__traceback__)
        return Response(status_code=HTTP_500_INTERNAL_SERVER_ERROR, content=e.__str__())


@router.post("/upload/")
async def upload_files(files_list: List[UploadFile] = File(...)):
    if not files_list:
        return Response(status_code=HTTP_400_BAD_REQUEST, content="Отсутствует файл")

    try:
        for file in files_list:
            file_path = path.join(upload_dir, file.filename)
            with open(file_path, "wb") as buffer:
                copyfileobj(file.file, buffer)

        return Response(status_code=HTTP_200_OK, content=f"{len(files_list)} файла успешно переданы")
    except PermissionError as e:
        print_exception(type(e), e, e.__traceback__)
        return Response(status_code=HTTP_403_FORBIDDEN, content="Не достаточно прав")
    except Exception as e:
        print_exception(type(e), e, e.__traceback__)
        return Response(status_code=HTTP_500_INTERNAL_SERVER_ERROR, content=e.__str__())

from fastapi import APIRouter, Request, UploadFile, File, Response, Depends
from typing import List
from shutil import copyfileobj
from os import system, path, environ
from starlette.responses import HTMLResponse
from traceback import print_exception

from starlette.status import HTTP_204_NO_CONTENT, HTTP_403_FORBIDDEN, HTTP_400_BAD_REQUEST, HTTP_200_OK

from . import env
from ..dependencies import is_authorized, get_auth_token
from ..config import UPLOAD_DIR

router = APIRouter(prefix="/panel", tags=["Home app"], dependencies=[Depends(get_auth_token)])


@router.get("")
def panel_page():
    template = env.get_template("panel.html")
    page = template.render()
    return HTMLResponse(page)


@router.post("/reboot")
def reboot_remote_device():
    system(f"echo \"{environ["PASSWORD"]}\" | sudo -S reboot")
    return Response(status_code=HTTP_204_NO_CONTENT)


@router.post("/upload")
async def upload_files(files_list: List[UploadFile] = File(...)):
    if not files_list:
        return Response(status_code=HTTP_400_BAD_REQUEST, content="Отсутствует файл")

    try:
        for file in files_list:
            file_path = path.join(UPLOAD_DIR, file.filename)
            with open(file_path, "wb") as buffer:
                copyfileobj(file.file, buffer)

        return Response(status_code=HTTP_200_OK, content=f"{len(files_list)} файла успешно переданы")
    except PermissionError as e:
        print_exception(type(e), e, e.__traceback__)
        return Response(status_code=HTTP_403_FORBIDDEN, content="Не достаточно прав")


@router.get("/status")
def check_connection_status(request: Request = Request):
    if is_authorized(request):
        return Response(status_code=HTTP_204_NO_CONTENT)
    return Response(status_code=HTTP_400_BAD_REQUEST)

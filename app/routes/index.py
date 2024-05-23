from fastapi import APIRouter
from fastapi.responses import HTMLResponse

from . import env

router = APIRouter()


@router.get("/")
def index(result: str = ""):
    template = env.get_template("index.html")
    page = template.render(result=result)
    return HTMLResponse(page)

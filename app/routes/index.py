from fastapi import APIRouter, Request
from fastapi.templating import Jinja2Templates

templates = Jinja2Templates(directory="templates/")
router = APIRouter()


@router.get("/")
def index(result: str = "", request: Request = Request):
    return templates.TemplateResponse("index.html", {"request": request, "result": result})

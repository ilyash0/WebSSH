from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse

from . import env
from ..dependencies import is_connected

router = APIRouter()


@router.get("/")
def index(alert_type: str = "warning", alert: str = "", request: Request = Request):
    template = env.get_template("index.html")
    user_agent = request.headers.get("user-agent")
    if not alert and is_connected(user_agent):
        alert = "У вас уже есть текущее соединение"
        alert_type = "info"
    page = template.render(alert_type=alert_type, alert=alert)
    return HTMLResponse(page)

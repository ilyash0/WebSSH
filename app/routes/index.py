from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse

from . import env
from ..dependencies import connections

router = APIRouter()


@router.get("/")
def index(alert_type: str = "warning", alert: str = "", request: Request = Request):
    template = env.get_template("index.html")
    user_agent = request.headers.get("user-agent")
    if not alert and connections.get(user_agent) and connections[user_agent].get_transport().active:
        alert = "У вас уже есть текущее соединение"
        alert_type = "info"
    page = template.render(alert_type=alert_type, alert=alert)
    return HTMLResponse(page)

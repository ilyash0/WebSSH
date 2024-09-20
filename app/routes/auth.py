from datetime import datetime, timedelta, UTC
from os import environ
from typing import Annotated

from fastapi import APIRouter, Request, Response, Depends
from fastapi.security import OAuth2PasswordRequestForm
from starlette.responses import RedirectResponse, HTMLResponse
from starlette.status import HTTP_204_NO_CONTENT, HTTP_400_BAD_REQUEST
from jose import jwt

from . import env
from ..config import ACCESS_TOKEN_EXPIRE_MINUTES, JWT_ALGORITHM, RATE_LIMIT
from ..dependencies import is_authorized, limiter, verify_recaptcha

router = APIRouter(tags=["Authentication"])


def create_access_token(data: dict) -> str:
    to_encode = data.copy()
    expire = datetime.now(UTC) + timedelta(seconds=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    encode_jwt = jwt.encode(to_encode, environ["SECRET_KEY"], algorithm=JWT_ALGORITHM)
    return encode_jwt


@router.get("/")
def index_page(alert_type: str = "warning", alert: str = "", request: Request = Request):
    template = env.get_template("index.html")
    if not alert and is_authorized(request):
        alert = "У вас уже есть текущее соединение"
        alert_type = "info"
    page = template.render(alert_type=alert_type, alert=alert, recaptcha_site_key=environ["RECAPTCHA_SITE_KEY"])
    return HTMLResponse(page)


@router.post("/login")
@limiter.limit(RATE_LIMIT)
def login(form_data: Annotated[OAuth2PasswordRequestForm, Depends()], request: Request = Request):
    password: str = form_data.password
    username: str = form_data.username
    recaptcha_token: str = form_data.client_secret

    if not verify_recaptcha(recaptcha_token):
        return Response(status_code=HTTP_400_BAD_REQUEST, content="Ошибка reCAPTCHA")

    if password != environ["PASSWORD"] or username != environ["USERNAME"]:
        return Response(status_code=HTTP_400_BAD_REQUEST, content="Неверное имя пользователя или пароль")

    access_token = create_access_token({})
    request.session["users_access_token"] = access_token
    limiter.reset()
    return Response(status_code=HTTP_204_NO_CONTENT)


@router.get("/logout")
def logout(request: Request = Request):
    if is_authorized(request):
        request.session.pop("users_access_token")

    return RedirectResponse(url="/")

from datetime import UTC, datetime
from os import environ

from fastapi import HTTPException, Request
from jose import JWTError, jwt
from requests import post
from starlette.status import HTTP_401_UNAUTHORIZED
from slowapi import Limiter
from slowapi.util import get_remote_address

from app.config import JWT_ALGORITHM, ENABLE_RECAPTCHA, RECAPTCHA_AVAILABLE_SCORE

limiter = Limiter(key_func=get_remote_address)


def verify_recaptcha(token: str) -> bool:
    # Firstly register here: https://www.google.com/recaptcha/admin/create
    if not ENABLE_RECAPTCHA:
        return True

    recaptcha_url = "https://www.google.com/recaptcha/api/siteverify"
    payload = {
        'secret': environ["RECAPTCHA_SECRET_KEY"],
        'response': token
    }
    response = post(recaptcha_url, data=payload)
    result = response.json()
    if result.get('success', False) and result.get("score") > RECAPTCHA_AVAILABLE_SCORE:
        return True
    return False


def get_auth_token(request: Request = Request) -> str:
    token = request.session.get('users_access_token')
    if not token:
        raise HTTPException(status_code=HTTP_401_UNAUTHORIZED, detail='Вы не авторизованы')

    try:
        payload = jwt.decode(token, environ["SECRET_KEY"], algorithms=[JWT_ALGORITHM])
    except JWTError:
        raise HTTPException(status_code=HTTP_401_UNAUTHORIZED, detail='Вы не авторизованы')

    expire = payload.get('exp')
    expire_time = datetime.fromtimestamp(int(expire), tz=UTC)
    if (not expire) or (expire_time < datetime.now(UTC)):
        raise HTTPException(status_code=HTTP_401_UNAUTHORIZED, detail='Время подключения истекло')

    return token


def is_authorized(request: Request) -> bool:
    try:
        token = get_auth_token(request)
        if token:
            return True
        return False
    except HTTPException:
        return False

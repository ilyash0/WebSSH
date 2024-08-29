from httpx import Response

from . import client, mock_env_vars, login, logout


def test_index_page_unauthorized(mock_env_vars):
    response: Response = client.get("/")
    assert response.status_code == 200
    assert ">У вас уже есть текущее соединение" not in response.text


def test_login_success(mock_env_vars):
    response: Response = client.post(
        "/login",
        data={"username": "testuser", "password": "testpassword"},
    )
    assert response.status_code == 204


def test_login_failure(mock_env_vars):
    response: Response = client.post(
        "/login",
        data={"username": "wronguser", "password": "wrongpassword"},
    )
    assert response.status_code == 400
    assert response.content.decode() == "Неверное имя пользователя или пароль"


def test_logout_authorized(mock_env_vars):
    login()
    response: Response = client.get("/logout")
    assert response.status_code == 200
    assert response.url == "http://testserver/"


def test_logout_unauthorized(mock_env_vars):
    response: Response = client.get("/logout")
    assert response.status_code == 200
    assert response.url == "http://testserver/"


def test_index_page_authorized(mock_env_vars, monkeypatch):
    login()
    response = client.get("/")
    assert response.status_code == 200
    assert ">У вас уже есть текущее соединение" in response.text
    logout()

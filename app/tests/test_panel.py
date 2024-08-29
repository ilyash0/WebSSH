from httpx import Response

from . import client, mock_env_vars, login, logout


def test_panel_page_authorized(mock_env_vars):
    login()
    response: Response = client.get("/panel")
    assert response.status_code == 200
    assert response.url == "http://testserver/panel"
    logout()


def test_panel_page_unauthorized(mock_env_vars):
    response = client.get("/panel")
    assert response.status_code == 200
    assert response.url == "http://testserver/?alert=Вы%20не%20авторизованы"


def test_reboot_remote_device_authorized(mock_env_vars):
    login()
    response = client.post("/panel/reboot")
    assert response.status_code == 204
    assert response.url == "http://testserver/panel/reboot"
    logout()


def test_reboot_remote_device_unauthorized(mock_env_vars):
    response = client.post("/panel/reboot")
    assert response.status_code == 200
    assert response.url == "http://testserver/?alert=Вы%20не%20авторизованы"


def test_upload_files_no_file(mock_env_vars):
    login()
    response = client.post("/panel/upload")
    assert response.status_code == 422
    logout()


def test_check_connection_status_authorized(mock_env_vars):
    login()
    response = client.get("/panel/status")
    assert response.status_code == 204
    logout()


def test_check_connection_status_unauthorized(mock_env_vars):
    response = client.get("/panel/status")
    assert response.status_code == 200
    assert response.url == "http://testserver/?alert=Вы%20не%20авторизованы"

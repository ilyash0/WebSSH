import os

import pytest
from fastapi.testclient import TestClient

import app.config as config
from app.main import app
client = TestClient(app)


@pytest.fixture
def mock_env_vars(monkeypatch):
    monkeypatch.setenv("SECRET_KEY", "testsecret")
    monkeypatch.setenv("PASSWORD", "testpassword")
    monkeypatch.setenv("USERNAME", "testuser")
    monkeypatch.setattr(config, "UPLOAD_DIR", "/home/ilya/BVR_Config")
    yield


def login():
    client.post(
        "/login",
        data={"username": "testuser", "password": "testpassword"},
    )


def logout():
    client.get("/logout")

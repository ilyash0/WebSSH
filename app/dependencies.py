from fastapi import Request

connections: list[str] = []
upload_dir = "/home/ilya"


def disconnect_session(user: str, request: Request):
    connections.remove(user)
    request.session.pop("password")


def is_connected(user: str):
    return user in connections

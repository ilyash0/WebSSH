from paramiko import SSHClient
from fastapi import Request

connections: dict[str, SSHClient] = {}


def disconnect_ssh(user_agent: str, request: Request):
    ssh = connections[user_agent]
    ssh.close()
    connections.pop(user_agent)
    request.session.pop("password")
    request.session.pop("username")
    request.session.pop("hostname")


def is_connected(user_agent: str):
    return connections.get(user_agent) and connections[user_agent].get_transport().active

connections: list[str] = []


def disconnect_session(user: str):
    connections.remove(user)


def is_connected(user: str):
    return user in connections

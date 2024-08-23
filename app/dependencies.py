from datetime import datetime

connections: list[dict[str, str | datetime]] = []


def get_connection_or_none(user_agent: str) -> dict[str, str | datetime] or None:
    return next((conn for conn in connections if conn["user_agent"] == user_agent), None)


def is_connected(user_agent: str) -> bool:
    return bool(get_connection_or_none(user_agent))

from paramiko import SSHClient

connections: dict[str, SSHClient] = {}

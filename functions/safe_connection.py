"""Connection helper that refuses non-public destination IP addresses."""

import ipaddress
import socket

from urllib3.util.connection import _set_socket_options


def create_safe_connection(
    address,
    timeout=socket._GLOBAL_DEFAULT_TIMEOUT,
    source_address=None,
    socket_options=None,
):
    host, port = address

    if host.startswith("[") and host.endswith("]"):
        host = host[1:-1]

    addresses = socket.getaddrinfo(
        host,
        port,
        type=socket.SOCK_STREAM,
    )

    if not addresses:
        raise OSError("No DNS addresses found")

    # Reject the entire hostname if any resolved address is non-public.
    for item in addresses:
        ip = ipaddress.ip_address(item[4][0])
        if not ip.is_global:
            raise OSError("Connection blocked: non-public destination IP")

    last_error = None

    for family, socktype, proto, _, sockaddr in addresses:
        sock = None

        try:
            sock = socket.socket(family, socktype, proto)
            _set_socket_options(sock, socket_options)

            if timeout is not socket._GLOBAL_DEFAULT_TIMEOUT:
                sock.settimeout(timeout)

            if source_address:
                sock.bind(source_address)

            # Connect to the already-validated numeric IP address.
            sock.connect(sockaddr)
            return sock

        except OSError as exc:
            last_error = exc
            if sock is not None:
                sock.close()

    raise OSError("Could not connect to validated destination") from last_error

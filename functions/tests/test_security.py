from unittest.mock import patch

import pytest

from safe_connection import create_safe_connection


@pytest.mark.parametrize(
    "host",
    [
        "127.0.0.1",
        "192.168.1.1",
        "10.0.0.1",
        "169.254.169.254",
        "::1",
    ],
)
def test_private_addresses_blocked(host):
    with patch("safe_connection.socket.socket") as mock_socket:
        with pytest.raises(OSError, match="non-public"):
            create_safe_connection((host, 80), timeout=1)

        mock_socket.assert_not_called()


def test_dns_resolution_to_private_ip_blocked():
    fake_dns = [
        (2, 1, 6, "", ("192.168.1.5", 443)),
    ]

    with (
        patch("safe_connection.socket.getaddrinfo", return_value=fake_dns),
        patch("safe_connection.socket.socket") as mock_socket,
    ):
        with pytest.raises(OSError, match="non-public"):
            create_safe_connection(("example.com", 443))

        mock_socket.assert_not_called()


@pytest.mark.parametrize(
    "url",
    [
        "http://127.0.0.1/",
        "https://127.0.0.1/",
        "http://169.254.169.254/",
    ],
)
def test_checker_blocks_private_destinations(url):
    from checker import check_url

    result = check_url(url, timeout=1)

    assert result["ok"] is False
    assert result["status_code"] is None
    assert result["error_type"] == "connection_error"


def test_checker_blocks_dns_rebinding():
    from checker import check_url

    fake_dns = [
        (2, 1, 6, "", ("169.254.169.254", 80)),
    ]

    with (
        patch("safe_connection.socket.getaddrinfo", return_value=fake_dns),
        patch("safe_connection.socket.socket") as mock_socket,
    ):
        result = check_url("http://example.com/", timeout=1)

        assert result["ok"] is False
        assert result["status_code"] is None
        assert result["error_type"] == "connection_error"
        mock_socket.assert_not_called()

from unittest.mock import Mock, patch

import requests

from checker import check_url, classify


def test_healthy_response():
    response = Mock(status_code=200)

    with patch("checker.requests.Session.get", return_value=response) as get:
        result = check_url("https://example.com", threshold_ms=10000)

    assert result["ok"] is True
    assert result["status_code"] == 200
    assert result["error_type"] is None
    assert result["latency_ms"] >= 0
    assert result["timestamp"]
    get.assert_called_once()


def test_http_500():
    response = Mock(status_code=500)

    with patch("checker.requests.Session.get", return_value=response):
        result = check_url("https://example.com")

    assert result["ok"] is False
    assert result["status_code"] == 500
    assert result["error_type"] == "http_5xx"


def test_timeout():
    with patch(
        "checker.requests.Session.get",
        side_effect=requests.exceptions.Timeout,
    ):
        result = check_url("https://example.com")

    assert result["ok"] is False
    assert result["status_code"] is None
    assert result["error_type"] == "timeout"


def test_ssl_error():
    with patch(
        "checker.requests.Session.get",
        side_effect=requests.exceptions.SSLError,
    ):
        result = check_url("https://example.com")

    assert result["ok"] is False
    assert result["error_type"] == "ssl_error"


def test_connection_error():
    with patch(
        "checker.requests.Session.get",
        side_effect=requests.exceptions.ConnectionError,
    ):
        result = check_url("https://example.com")

    assert result["ok"] is False
    assert result["error_type"] == "connection_error"


def test_classification():
    assert classify(200, 100, 1000) is None
    assert classify(404, 100, 1000) == "http_4xx"
    assert classify(500, 100, 1000) == "http_5xx"
    assert classify(200, 1500, 1000) == "slow"

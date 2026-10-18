import json
from unittest.mock import patch

import azure.functions as func

from function_app import add_target, ping


def make_request(method, url, body=None):
    return func.HttpRequest(
        method=method,
        url=url,
        body=json.dumps(body).encode() if body is not None else b"",
    )


def test_ping():
    request = make_request("GET", "http://localhost:7071/api/ping")
    response = ping(request)

    assert response.status_code == 200
    assert json.loads(response.get_body()) == {"status": "ok"}


def test_add_target_rejects_invalid_json():
    request = func.HttpRequest(
        method="POST",
        url="http://localhost:7071/api/targets",
        body=b"not valid json",
    )

    response = add_target(request)

    assert response.status_code == 400


def test_add_target_rejects_private_ip():
    request = make_request(
        "POST",
        "http://localhost:7071/api/targets",
        {"name": "Local", "url": "http://127.0.0.1"},
    )

    response = add_target(request)

    assert response.status_code == 400


@patch("function_app.monitor.process_target")
@patch("function_app.store.upsert_target")
def test_add_target_success(upsert_target, process_target):
    request = make_request(
        "POST",
        "http://localhost:7071/api/targets",
        {"name": "Example", "url": "https://example.com"},
    )

    response = add_target(request)

    assert response.status_code == 201
    assert json.loads(response.get_body())["name"] == "Example"
    upsert_target.assert_called_once()
    process_target.assert_called_once()


@patch("function_app.store.checks_since")
@patch("function_app.store.list_targets")
def test_get_status(list_targets, checks_since):
    from function_app import get_status

    list_targets.return_value = [{
        "id": "target-1",
        "name": "Example",
        "url": "https://example.com",
        "state": "up",
        "last_status_code": 200,
        "last_latency_ms": 120,
        "last_checked": "2026-10-19T10:00:00+00:00",
    }]
    checks_since.return_value = [
        {"ok": True},
        {"ok": True},
        {"ok": False},
    ]

    request = make_request("GET", "http://localhost:7071/api/status")
    response = get_status(request)
    data = json.loads(response.get_body())

    assert response.status_code == 200
    assert len(data) == 1
    assert data[0]["name"] == "Example"
    assert data[0]["ok"] is True
    assert data[0]["uptime_24h"] == 66.67


def test_get_history_requires_target_id():
    from function_app import get_history

    request = make_request("GET", "http://localhost:7071/api/history")
    response = get_history(request)

    assert response.status_code == 400


@patch("function_app.store.checks_since")
def test_get_history_success(checks_since):
    from function_app import get_history

    checks_since.return_value = [{
        "timestamp": "2026-10-19T10:00:00+00:00",
        "latency_ms": 120,
        "ok": True,
    }]

    request = func.HttpRequest(
        method="GET",
        url="http://localhost:7071/api/history",
        params={"target_id": "target-1", "hours": "24"},
        body=b"",
    )

    response = get_history(request)
    data = json.loads(response.get_body())

    assert response.status_code == 200
    assert len(data) == 1
    assert data[0]["latency_ms"] == 120


@patch("function_app.store.list_incidents")
def test_get_incidents(list_incidents):
    from function_app import get_incidents

    list_incidents.return_value = [{
        "id": "incident-1",
        "name": "Example",
        "started_at": "2026-10-19T10:00:00+00:00",
        "resolved_at": None,
    }]

    request = make_request("GET", "http://localhost:7071/api/incidents")
    response = get_incidents(request)
    data = json.loads(response.get_body())

    assert response.status_code == 200
    assert len(data) == 1
    assert data[0]["id"] == "incident-1"

from unittest.mock import patch

import monitor


def sample_target(state="up"):
    return {
        "id": "target-1",
        "name": "Example",
        "url": "https://example.com",
        "state": state,
        "latency_threshold_ms": 1000,
        "alert_email": "test@example.com",
    }


def sample_result(ok):
    return {
        "ok": ok,
        "status_code": 200 if ok else 500,
        "latency_ms": 100,
        "error_type": None if ok else "http_5xx",
        "timestamp": "2026-10-19T10:00:00+00:00",
    }


@patch("monitor.alerts.send_email")
@patch("monitor.store")
@patch("monitor.checker.check_url")
def test_outage_creates_incident(check_url, store, send_email):
    check_url.return_value = sample_result(False)
    target = sample_target("up")

    transition = monitor.process_target(target)

    assert transition == "went_down"
    assert target["state"] == "down"
    assert target["open_incident_id"]
    store.add_check.assert_called_once()
    store.create_incident.assert_called_once()
    store.upsert_target.assert_called_once()
    send_email.assert_called_once()


@patch("monitor.alerts.send_email")
@patch("monitor.store")
@patch("monitor.checker.check_url")
def test_staying_down_does_not_repeat_alert(check_url, store, send_email):
    check_url.return_value = sample_result(False)
    target = sample_target("down")
    target["open_incident_id"] = "incident-1"

    transition = monitor.process_target(target)

    assert transition is None
    store.create_incident.assert_not_called()
    send_email.assert_not_called()
    assert target["open_incident_id"] == "incident-1"


@patch("monitor.alerts.send_email")
@patch("monitor.store")
@patch("monitor.checker.check_url")
def test_recovery_resolves_incident(check_url, store, send_email):
    check_url.return_value = sample_result(True)
    target = sample_target("down")
    target["open_incident_id"] = "incident-1"

    transition = monitor.process_target(target)

    assert transition == "recovered"
    assert target["state"] == "up"
    assert target["open_incident_id"] is None
    store.resolve_incident.assert_called_once_with(
        "target-1",
        "incident-1",
        "2026-10-19T10:00:00+00:00",
    )
    send_email.assert_called_once()


def test_uptime_percentage():
    checks = [{"ok": True}, {"ok": True}, {"ok": False}]
    assert monitor.uptime_pct(checks) == 66.67
    assert monitor.uptime_pct([]) is None


def test_target_validation():
    valid, error = monitor.validate_target_payload({
        "name": "Example",
        "url": "https://example.com",
    })
    assert error is None
    assert valid["latency_threshold_ms"] == 1000

    invalid, error = monitor.validate_target_payload({
        "name": "Local",
        "url": "http://127.0.0.1",
    })
    assert invalid is None
    assert error is not None

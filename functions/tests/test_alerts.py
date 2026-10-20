from unittest.mock import patch

from alerts import (
    decide_transition,
    down_message,
    recovered_message,
    send_email,
)


def test_website_goes_down():
    assert decide_transition("up", False) == "went_down"


def test_website_stays_down():
    assert decide_transition("down", False) is None


def test_website_recovers():
    assert decide_transition("down", True) == "recovered"


def test_website_stays_up():
    assert decide_transition("up", True) is None


def test_first_failed_check():
    assert decide_transition("unknown", False) == "went_down"


def test_alert_messages():
    target = {
        "name": "Google",
        "url": "https://google.com",
    }
    result = {
        "error_type": "timeout",
        "status_code": None,
        "latency_ms": 10000,
        "timestamp": "2026-10-19T10:00:00+00:00",
    }

    down_subject, down_body = down_message(target, result)
    recovered_subject, recovered_body = recovered_message(target, result)

    assert "[DOWN]" in down_subject
    assert "timeout" in down_body
    assert "[RECOVERED]" in recovered_subject
    assert "Google" in recovered_body


def test_email_without_configuration():
    with patch.dict("os.environ", {}, clear=True):
        assert send_email("test@example.com", "Test", "Hello") is False

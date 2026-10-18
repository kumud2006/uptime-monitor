import logging
import os
import smtplib
from email.message import EmailMessage

logger = logging.getLogger(__name__)


def decide_transition(previous_state, ok):
    """Return the state change, or None if no alert is needed."""
    if ok and previous_state == "down":
        return "recovered"
    if not ok and previous_state != "down":
        return "went_down"
    return None


def down_message(target, result):
    subject = f"[DOWN] {target['name']} is not responding"
    body = (
        f"{target['name']} ({target['url']}) failed its health check.\n\n"
        f"Problem: {result['error_type']}\n"
        f"HTTP status: {result['status_code']}\n"
        f"Response time: {result['latency_ms']} ms\n"
        f"Time (UTC): {result['timestamp']}\n"
    )
    return subject, body


def recovered_message(target, result):
    subject = f"[RECOVERED] {target['name']} is back up"
    body = (
        f"{target['name']} ({target['url']}) is responding normally again.\n\n"
        f"HTTP status: {result['status_code']}\n"
        f"Response time: {result['latency_ms']} ms\n"
        f"Time (UTC): {result['timestamp']}\n"
    )
    return subject, body


def send_email(to_addr, subject, body):
    """Send an email through SMTP. Return True if sent successfully."""
    host = os.environ.get("SMTP_HOST")
    user = os.environ.get("SMTP_USER")
    password = os.environ.get("SMTP_PASSWORD")

    if not (host and user and password and to_addr):
        logger.warning("SMTP not configured, alert not emailed: %s", subject)
        return False

    message = EmailMessage()
    message["From"] = user
    message["To"] = to_addr
    message["Subject"] = subject
    message.set_content(body)

    try:
        with smtplib.SMTP(
            host,
            int(os.environ.get("SMTP_PORT", "587")),
            timeout=15,
        ) as server:
            server.starttls()
            server.login(user, password)
            server.send_message(message)

        logger.info("Alert emailed to %s: %s", to_addr, subject)
        return True

    except (OSError, smtplib.SMTPException):
        logger.exception("Failed to send alert email")
        return False

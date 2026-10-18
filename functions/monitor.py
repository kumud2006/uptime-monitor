import ipaddress
import logging
import os
import uuid
from concurrent.futures import ThreadPoolExecutor
from datetime import UTC, datetime, timedelta
from urllib.parse import urlparse

import alerts
import checker
import store

logger = logging.getLogger(__name__)


def iso_hours_ago(hours):
    moment = datetime.now(UTC) - timedelta(hours=hours)
    return moment.isoformat(timespec="seconds")


def uptime_pct(checks):
    """Percentage of successful checks, or None when there is no data."""
    if not checks:
        return None
    ok_count = sum(1 for c in checks if c.get("ok"))
    return round(100 * ok_count / len(checks), 2)


def _is_private_host(host):
    if host == "localhost":
        return True
    try:
        ip = ipaddress.ip_address(host)
    except ValueError:
        return False
    return not ip.is_global


def validate_target_payload(data):
    """Return (clean_dict, None) if valid, otherwise (None, error)."""
    if not isinstance(data, dict):
        return None, "Body must be a JSON object"

    name = str(data.get("name", "")).strip()
    url = str(data.get("url", "")).strip()

    if not name:
        return None, "name is required"
    if not url.startswith(("http://", "https://")):
        return None, "url must start with http:// or https://"

    try:
        host = urlparse(url).hostname
    except ValueError:
        return None, "Invalid URL"

    if not host or _is_private_host(host.lower()):
        return None, "url must point to a public website"

    if not is_safe_target_url(url):
        return None, "url must point to a safe, publicly reachable website"

    try:
        threshold = int(data.get("latency_threshold_ms", 1000))
    except (TypeError, ValueError):
        return None, "latency_threshold_ms must be a whole number"

    if threshold <= 0:
        return None, "latency_threshold_ms must be greater than 0"

    clean = {
        "name": name,
        "url": url,
        "latency_threshold_ms": threshold,
        "alert_email": str(data.get("alert_email", "")).strip(),
    }
    return clean, None


def process_target(target):
    """Check one target, store the result, and handle state changes."""
    if not is_safe_target_url(target["url"]):
        raise ValueError("Unsafe target URL: monitoring request blocked")

    result = checker.check_url(
        target["url"],
        target.get("latency_threshold_ms", 1000),
    )
    transition = alerts.decide_transition(
        target.get("state", "unknown"),
        result["ok"],
    )

    store.add_check({
        "id": str(uuid.uuid4()),
        "target_id": target["id"],
        **result,
    })

    target["state"] = "up" if result["ok"] else "down"
    target["last_checked"] = result["timestamp"]
    target["last_status_code"] = result["status_code"]
    target["last_latency_ms"] = result["latency_ms"]
    target["last_error_type"] = result["error_type"]

    recipient = target.get("alert_email") or os.environ.get("ALERT_EMAIL")

    if transition == "went_down":
        incident = {
            "id": str(uuid.uuid4()),
            "target_id": target["id"],
            "name": target["name"],
            "started_at": result["timestamp"],
            "resolved_at": None,
            "error_type": result["error_type"],
        }
        store.create_incident(incident)
        target["open_incident_id"] = incident["id"]

        subject, body = alerts.down_message(target, result)
        alerts.send_email(recipient, subject, body)

    elif transition == "recovered":
        if target.get("open_incident_id"):
            store.resolve_incident(
                target["id"],
                target["open_incident_id"],
                result["timestamp"],
            )

        target["open_incident_id"] = None
        subject, body = alerts.recovered_message(target, result)
        alerts.send_email(recipient, subject, body)

    store.upsert_target(target)
    return transition


def run_all_checks():
    """Check every saved target concurrently."""
    targets = store.list_targets()
    logger.info("Checking %d targets", len(targets))

    if not targets:
        return 0

    def safe(target):
        try:
            return process_target(target)
        except Exception:
            logger.exception("Check failed for %s", target.get("url"))
            return None

    with ThreadPoolExecutor(max_workers=10) as pool:
        list(pool.map(safe, targets))

    return len(targets)


def is_safe_target_url(url):
    """Check whether a URL resolves only to public IP addresses."""
    import ipaddress
    import socket
    from urllib.parse import urlsplit

    try:
        parsed = urlsplit(url)

        if parsed.scheme not in ("http", "https"):
            return False

        if not parsed.hostname or parsed.username or parsed.password:
            return False

        if parsed.port not in (None, 80, 443):
            return False

        hostname = parsed.hostname

        if hostname.lower() == "localhost":
            return False

        addresses = socket.getaddrinfo(
            hostname,
            parsed.port or (443 if parsed.scheme == "https" else 80),
            type=socket.SOCK_STREAM,
        )

        if not addresses:
            return False

        for address in addresses:
            ip = ipaddress.ip_address(address[4][0])
            if not ip.is_global:
                return False

        return True

    except (ValueError, OSError):
        return False

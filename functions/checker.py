import logging
import time
from datetime import UTC, datetime

import requests

from safe_adapter import SafeHTTPAdapter

logger = logging.getLogger(__name__)

TIMEOUT_SECONDS = 10


def utc_now_iso():
    return datetime.now(UTC).isoformat(timespec="seconds")


def classify(status_code, latency_ms, threshold_ms):
    """Return an error type string, or None when the site is healthy."""
    if status_code >= 500:
        return "http_5xx"
    if status_code >= 400:
        return "http_4xx"
    if latency_ms > threshold_ms:
        return "slow"
    return None


def check_url(url, threshold_ms=1000, timeout=TIMEOUT_SECONDS):
    """Request the URL once and describe what happened."""
    started = time.perf_counter()
    status_code = None
    error_type = None

    try:
        with requests.Session() as session:
            session.trust_env = False
            session.mount("http://", SafeHTTPAdapter())
            session.mount("https://", SafeHTTPAdapter())

            response = session.get(
                url,
                timeout=timeout,
                allow_redirects=False,
                headers={"User-Agent": "UptimeMonitor/1.0"},
            )
        status_code = response.status_code
        latency_ms = int((time.perf_counter() - started) * 1000)
        error_type = classify(status_code, latency_ms, threshold_ms)
    except requests.exceptions.SSLError:
        error_type = "ssl_error"
    except requests.exceptions.Timeout:
        error_type = "timeout"
    except requests.exceptions.RequestException:
        error_type = "connection_error"

    latency_ms = int((time.perf_counter() - started) * 1000)

    return {
        "status_code": status_code,
        "latency_ms": latency_ms,
        "ok": error_type is None,
        "error_type": error_type,
        "timestamp": utc_now_iso(),
    }

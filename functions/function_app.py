import json
import logging
import uuid

import azure.functions as func

import checker
import monitor
import store

logger = logging.getLogger(__name__)

app = func.FunctionApp()


def _json(data, status=200):
    return func.HttpResponse(
        json.dumps(data),
        status_code=status,
        mimetype="application/json",
    )


@app.timer_trigger(
    schedule="0 */5 * * * *",
    arg_name="timer",
    run_on_startup=False,
)
def health_check(timer: func.TimerRequest) -> None:
    count = monitor.run_all_checks()
    logger.info("Health check finished for %d targets", count)


@app.route(route="ping", methods=["GET"], auth_level=func.AuthLevel.ANONYMOUS)
def ping(req: func.HttpRequest) -> func.HttpResponse:
    return _json({"status": "ok"})


@app.route(route="status", methods=["GET"], auth_level=func.AuthLevel.ANONYMOUS)
def get_status(req: func.HttpRequest) -> func.HttpResponse:
    since = monitor.iso_hours_ago(24)
    rows = []

    for target in store.list_targets():
        checks = store.checks_since(target["id"], since)
        rows.append({
            "id": target["id"],
            "name": target["name"],
            "url": target["url"],
            "ok": target.get("state") == "up",
            "status_code": target.get("last_status_code"),
            "latency_ms": target.get("last_latency_ms"),
            "last_checked": target.get("last_checked"),
            "uptime_24h": monitor.uptime_pct(checks),
        })

    return _json(rows)


@app.route(route="history", methods=["GET"], auth_level=func.AuthLevel.ANONYMOUS)
def get_history(req: func.HttpRequest) -> func.HttpResponse:
    target_id = req.params.get("target_id")

    if not target_id:
        return _json({"error": "target_id is required"}, 400)

    try:
        hours = int(req.params.get("hours", "24"))
    except ValueError:
        return _json({"error": "hours must be a number"}, 400)

    hours = max(1, min(hours, 168))

    return _json(
        store.checks_since(target_id, monitor.iso_hours_ago(hours))
    )


@app.route(route="incidents", methods=["GET"], auth_level=func.AuthLevel.ANONYMOUS)
def get_incidents(req: func.HttpRequest) -> func.HttpResponse:
    return _json(store.list_incidents())


@app.route(route="targets", methods=["POST"], auth_level=func.AuthLevel.FUNCTION)
def add_target(req: func.HttpRequest) -> func.HttpResponse:
    try:
        data = req.get_json()
    except ValueError:
        return _json({"error": "Body must be valid JSON"}, 400)

    clean, error = monitor.validate_target_payload(data)

    if error:
        return _json({"error": error}, 400)

    doc = {
        "id": str(uuid.uuid4()),
        **clean,
        "state": "unknown",
        "open_incident_id": None,
        "created_at": checker.utc_now_iso(),
    }

    store.upsert_target(doc)

    try:
        monitor.process_target(doc)
    except Exception:
        logger.exception("First check failed for %s", doc["url"])

    return _json({
        "id": doc["id"],
        "name": doc["name"],
        "url": doc["url"],
    }, 201)

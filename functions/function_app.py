import json
import logging

import azure.functions as func

app = func.FunctionApp()


@app.timer_trigger(schedule="0 */5 * * * *", arg_name="timer", run_on_startup=False)
def health_check(timer: func.TimerRequest) -> None:
    logging.info("placeholder timer fired")


@app.route(route="ping", auth_level=func.AuthLevel.ANONYMOUS)
def ping(req: func.HttpRequest) -> func.HttpResponse:
    return func.HttpResponse(json.dumps({"status": "ok"}), mimetype="application/json")


# Deliberate failure to test the alert. Delete before the final demo.
@app.route(route="boom", auth_level=func.AuthLevel.ANONYMOUS)
def boom(req: func.HttpRequest) -> func.HttpResponse:
    raise RuntimeError("test exception for alerting")
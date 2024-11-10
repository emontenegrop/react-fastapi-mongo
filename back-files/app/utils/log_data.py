import datetime
from typing import Any, Dict

from app.config.settings import Settings
from app.logger import logger
from fastapi import Request
import httpx

module_name = "back-files"
status_failure = "failure"
status_success = "success"


def create_log_error(
    data_headers: Dict[str, Any],
    code: int,
    detail: Any,
    message: Any,
    time_response: Any,
):
    "Crea el registro en el log de auditoria"
    try:
        now = datetime.datetime.now()
        data = {
            "timestamp": now.strftime("%d/%m/%Y %H:%M:%S"),
            "application_code": data_headers.get("x_application_code"),
            "status": status_failure,
            "event_id": data_headers.get("x_event_id"),
            "error": {
                "time": time_response,
                "status_code": code,
                "description": detail,
                "traceback": message,
            },
            "actor": {
                "user_name": data_headers.get("x_user_name"),
                "client": module_name,
                "ip_address": data_headers.get("x_ip_address"),
                "api_path": data_headers.get("url"),
            },
        }
        headers = {"Content-Type": "application/json"}
        body = data        
        httpx.post(
            str(Settings.BACK_LOGS),
            json=body,
            headers=headers,
            timeout=Settings.TIMEOUT,
        )
        logger.debug(data)
    except Exception as exc:
        logger.debug(f"Error en el servicio de auditoria {exc}")


def create_log_event(data_headers: Dict[str, Any], code: int, message: Any):
    "Crea el registro en el log de auditoria"
    try:
        now = datetime.datetime.now()
        data = {
            "timestamp": now.strftime("%d/%m/%Y %H:%M:%S"),
            "application_code": data_headers.get("x_application_code"),
            "status": "success",
            "event_id": data_headers.get("x_event_id"),
            "status_code": code,
            "actor": {
                "user_name": data_headers.get("x_user_name"),
                "client": module_name,
                "ip_address": data_headers.get("x_ip_address"),
                "api_path": data_headers.get("url"),
            },
            "event": {
                "parameters": data_headers.get("parameters"),
                "object_type": data_headers.get("x-object-type"),
                "response": message,
            },
        }
        headers = {"Content-Type": "application/json"}
        body = data
        httpx.post(
            str(Settings.BACK_LOGS),
            json=body,
            headers=headers,
            timeout=Settings.TIMEOUT,
        )
        logger.debug(data)
    except Exception as exc:
        logger.debug(f"Error en el servicio de auditoria {exc}")


def data_headers(request: Request):  # type: ignore

    try:
        headers_log = request.headers
        data = {
            "x_user_name": headers_log.get("x-user-name"),
            "x_ip_address": headers_log.get("x-ip-address"),
            "x_event_id": headers_log.get("x-event-id"),
            "x_application_code": headers_log.get("x-application-code"),
            "url": request.url.path,
        }
    except Exception as exc:
        logger.debug(f"Error en el servicio de auditoria {exc}")
        return {}

    return data

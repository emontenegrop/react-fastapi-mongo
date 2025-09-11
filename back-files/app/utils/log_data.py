import datetime
from typing import Any, Dict
import httpx
from tenacity import retry, stop_after_attempt, wait_exponential

from app.config.settings import settings
from app.logger import logger
from app.utils.circuit_breaker import with_circuit_breaker, CircuitBreakerError
from app.utils.structured_logger import performance_logger
from fastapi import Request

module_name = "back-files"
status_failure = "failure"
status_success = "success"


@with_circuit_breaker(
    name="back-logs-service",
    failure_threshold=3,
    recovery_timeout=30,
    expected_exception=(httpx.RequestError, httpx.HTTPStatusError)
)
@retry(
    stop=stop_after_attempt(2),
    wait=wait_exponential(multiplier=1, min=1, max=5),
    retry=lambda retry_state: isinstance(retry_state.outcome.exception(), (httpx.RequestError, httpx.TimeoutException))
)
async def _send_log_to_service(data: Dict[str, Any]) -> bool:
    """
    Send log data to the logging service with circuit breaker and retry logic.
    
    Returns:
        bool: True if successful, False otherwise
    """
    headers = {"Content-Type": "application/json"}
    
    start_time = datetime.datetime.now()
    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(
                str(settings.BACK_LOGS),
                json=data,
                headers=headers,
                timeout=settings.TIMEOUT
            )
            response.raise_for_status()
            
            # Log performance metrics
            duration = (datetime.datetime.now() - start_time).total_seconds() * 1000
            performance_logger.log_external_api_call(
                service="back-logs",
                endpoint="/log_data",
                method="POST",
                duration_ms=duration,
                status_code=response.status_code,
                success=True
            )
            
            return True
            
    except (httpx.RequestError, httpx.HTTPStatusError) as e:
        duration = (datetime.datetime.now() - start_time).total_seconds() * 1000
        performance_logger.log_external_api_call(
            service="back-logs",
            endpoint="/log_data", 
            method="POST",
            duration_ms=duration,
            status_code=getattr(e, 'response', {}).get('status_code'),
            success=False
        )
        raise


async def create_log_error(
    data_headers: Dict[str, Any],
    code: int,
    detail: Any,
    message: Any,
    time_response: Any,
):
    """Create error log entry in the audit service"""
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
        
        # Try to send to logging service
        try:
            await _send_log_to_service(data)
            logger.debug("Error log sent to audit service", extra={"audit_data": data})
        except CircuitBreakerError:
            logger.warning("Audit service unavailable (circuit breaker open)")
        except Exception as exc:
            logger.error(f"Failed to send error log to audit service: {exc}")
        
        # Always log locally regardless of external service status
        logger.error("Application error logged", extra={"audit_data": data})
        
    except Exception as exc:
        logger.error(f"Error in audit logging system: {exc}")


async def create_log_event(data_headers: Dict[str, Any], code: int, message: Any):
    """Create success log entry in the audit service"""
    try:
        now = datetime.datetime.now()
        data = {
            "timestamp": now.strftime("%d/%m/%Y %H:%M:%S"),
            "application_code": data_headers.get("x_application_code"),
            "status": status_success,
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
        
        # Try to send to logging service
        try:
            await _send_log_to_service(data)
            logger.debug("Event log sent to audit service", extra={"audit_data": data})
        except CircuitBreakerError:
            logger.warning("Audit service unavailable (circuit breaker open)")
        except Exception as exc:
            logger.warning(f"Failed to send event log to audit service: {exc}")
        
        # Always log locally regardless of external service status
        logger.info("Application event logged", extra={"audit_data": data})
        
    except Exception as exc:
        logger.error(f"Error in audit logging system: {exc}")


def data_headers(request: Request) -> Dict[str, Any]:
    """Extract relevant headers for audit logging"""
    try:
        headers_log = request.headers
        data = {
            "x_user_name": headers_log.get("x-user-name"),
            "x_ip_address": headers_log.get("x-ip-address") or request.client.host if request.client else None,
            "x_event_id": headers_log.get("x-event-id"),
            "x_application_code": headers_log.get("x-application-code"),
            "url": request.url.path,
            "method": request.method,
            "user_agent": headers_log.get("user-agent"),
        }
        return data
    except Exception as exc:
        logger.error(f"Error extracting headers for audit: {exc}")
        return {}

"""Structured logging configuration using structlog"""

import sys
import logging
import structlog
from typing import Any, Dict, Optional
from datetime import datetime
from app.config.settings import settings


def setup_logging(log_level: Optional[str] = None) -> None:
    """
    Configure structured logging with JSON output for production
    and human-readable output for development.
    """
    level = log_level or settings.LOG_LEVEL
    
    # Configure structlog processors
    shared_processors = [
        structlog.stdlib.filter_by_level,
        structlog.stdlib.add_logger_name,
        structlog.stdlib.add_log_level,
        structlog.stdlib.PositionalArgumentsFormatter(),
        structlog.processors.TimeStamper(fmt="ISO"),
        structlog.processors.StackInfoRenderer(),
        structlog.processors.format_exc_info,
        structlog.processors.UnicodeDecoder(),
        add_service_context,
    ]
    
    # Configure different formatters for different environments
    if settings.LOG_LEVEL == "DEBUG":
        # Human-readable format for development
        formatter = structlog.dev.ConsoleRenderer(colors=True)
    else:
        # JSON format for production
        formatter = structlog.processors.JSONRenderer()
    
    structlog.configure(
        processors=shared_processors + [
            structlog.stdlib.ProcessorFormatter.wrap_for_formatter,
        ],
        context_class=dict,
        logger_factory=structlog.stdlib.LoggerFactory(),
        wrapper_class=structlog.stdlib.BoundLogger,
        cache_logger_on_first_use=True,
    )
    
    # Configure standard library logging
    logging.basicConfig(
        format="%(message)s",
        stream=sys.stdout,
        level=getattr(logging, level.upper()),
    )
    
    # Set the formatter for the structlog processor
    handler = logging.StreamHandler()
    handler.setFormatter(structlog.stdlib.ProcessorFormatter(
        processor=formatter,
    ))
    
    root_logger = logging.getLogger()
    root_logger.handlers = [handler]
    root_logger.setLevel(getattr(logging, level.upper()))
    
    # Reduce noise from third-party libraries
    logging.getLogger("uvicorn.access").setLevel(logging.WARNING)
    logging.getLogger("motor").setLevel(logging.INFO)
    logging.getLogger("httpx").setLevel(logging.WARNING)


def add_service_context(logger: Any, method_name: str, event_dict: Dict[str, Any]) -> Dict[str, Any]:
    """Add service-specific context to log entries"""
    event_dict.update({
        "service": "back-files",
        "version": "1.0.0",
        "environment": "development" if settings.LOG_LEVEL == "DEBUG" else "production"
    })
    return event_dict


def get_logger(name: Optional[str] = None) -> structlog.BoundLogger:
    """Get a structured logger instance"""
    return structlog.get_logger(name)


class RequestLogger:
    """Context manager for request logging"""
    
    def __init__(self, request_id: str, method: str, path: str, user_id: Optional[str] = None):
        self.logger = get_logger("request")
        self.request_id = request_id
        self.method = method
        self.path = path
        self.user_id = user_id
        self.start_time = datetime.now()
    
    def __enter__(self):
        self.logger.info(
            "Request started",
            request_id=self.request_id,
            method=self.method,
            path=self.path,
            user_id=self.user_id
        )
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        duration = (datetime.now() - self.start_time).total_seconds()
        
        if exc_type is None:
            self.logger.info(
                "Request completed",
                request_id=self.request_id,
                method=self.method,
                path=self.path,
                user_id=self.user_id,
                duration_seconds=duration
            )
        else:
            self.logger.error(
                "Request failed",
                request_id=self.request_id,
                method=self.method,
                path=self.path,
                user_id=self.user_id,
                duration_seconds=duration,
                error=str(exc_val),
                error_type=exc_type.__name__ if exc_type else None
            )
    
    def log_event(self, event: str, **kwargs):
        """Log a custom event within the request context"""
        self.logger.info(
            event,
            request_id=self.request_id,
            method=self.method,
            path=self.path,
            user_id=self.user_id,
            **kwargs
        )


class SecurityLogger:
    """Specialized logger for security events"""
    
    def __init__(self):
        self.logger = get_logger("security")
    
    def log_authentication_attempt(
        self, 
        email: str, 
        success: bool, 
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None
    ):
        """Log authentication attempts"""
        self.logger.info(
            "Authentication attempt",
            email=email,
            success=success,
            ip_address=ip_address,
            user_agent=user_agent,
            event_type="auth_attempt"
        )
    
    def log_file_access(
        self,
        file_id: str,
        user_id: int,
        action: str,  # "upload", "download", "delete"
        ip_address: Optional[str] = None,
        success: bool = True
    ):
        """Log file access events"""
        self.logger.info(
            "File access",
            file_id=file_id,
            user_id=user_id,
            action=action,
            ip_address=ip_address,
            success=success,
            event_type="file_access"
        )
    
    def log_security_violation(
        self,
        violation_type: str,
        details: Dict[str, Any],
        severity: str = "medium",  # "low", "medium", "high", "critical"
        ip_address: Optional[str] = None
    ):
        """Log security violations"""
        self.logger.warning(
            "Security violation",
            violation_type=violation_type,
            severity=severity,
            ip_address=ip_address,
            event_type="security_violation",
            **details
        )


class PerformanceLogger:
    """Logger for performance metrics"""
    
    def __init__(self):
        self.logger = get_logger("performance")
    
    def log_database_query(
        self,
        collection: str,
        operation: str,
        duration_ms: float,
        record_count: Optional[int] = None
    ):
        """Log database query performance"""
        self.logger.info(
            "Database query",
            collection=collection,
            operation=operation,
            duration_ms=duration_ms,
            record_count=record_count,
            event_type="db_query"
        )
    
    def log_external_api_call(
        self,
        service: str,
        endpoint: str,
        method: str,
        duration_ms: float,
        status_code: Optional[int] = None,
        success: bool = True
    ):
        """Log external API call performance"""
        self.logger.info(
            "External API call",
            service=service,
            endpoint=endpoint,
            method=method,
            duration_ms=duration_ms,
            status_code=status_code,
            success=success,
            event_type="api_call"
        )


# Initialize loggers
security_logger = SecurityLogger()
performance_logger = PerformanceLogger()

# Setup logging on import
setup_logging()
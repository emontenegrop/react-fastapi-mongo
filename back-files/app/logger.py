"""Legacy logger for backward compatibility"""

import logging
from app.utils.structured_logger import get_logger, setup_logging
from app.config.settings import settings

# Ensure structured logging is set up
setup_logging()

# Create a structured logger instance
structured_logger = get_logger("app")

# Create a legacy logger that wraps the structured logger for backward compatibility
class LegacyLoggerAdapter(logging.LoggerAdapter):
    """Adapter to make structured logger compatible with legacy logging calls"""
    
    def __init__(self):
        # Create a dummy logger for the adapter
        legacy_logger = logging.getLogger("legacy")
        super().__init__(legacy_logger, {})
        self._structured_logger = structured_logger
    
    def debug(self, msg, *args, **kwargs):
        self._structured_logger.debug(str(msg) % args if args else str(msg), **kwargs)
    
    def info(self, msg, *args, **kwargs):
        self._structured_logger.info(str(msg) % args if args else str(msg), **kwargs)
    
    def warning(self, msg, *args, **kwargs):
        self._structured_logger.warning(str(msg) % args if args else str(msg), **kwargs)
    
    def error(self, msg, *args, **kwargs):
        self._structured_logger.error(str(msg) % args if args else str(msg), **kwargs)
    
    def critical(self, msg, *args, **kwargs):
        self._structured_logger.critical(str(msg) % args if args else str(msg), **kwargs)

# Create the legacy logger instance
logger = LegacyLoggerAdapter()

# Also expose the structured logger for new code
__all__ = ['logger', 'structured_logger']

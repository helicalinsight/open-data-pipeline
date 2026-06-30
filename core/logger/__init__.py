import logging
import functools
import re

# Default logger if none is provided/found
default_logger = logging.getLogger('openDataPipelineCoreLogger')

class Logger:
    """
    Logger utility class. 
    Can use a global logger or an instance-specific logger property.
    """

    @staticmethod
    def generate(func):
        """
        Decorator to log function start/end.
        Tries to use 'self.logger' if available, else falls back to default_logger.
        """
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            # Attempt to resolve a specific logger
            log = default_logger
            class_name = "Unknown"

            if args:
                instance = args[0]
                class_name = instance.__class__.__name__
                # Check if the instance has a 'logger' attribute
                if hasattr(instance, 'logger') and isinstance(instance.logger, logging.Logger):
                    log = instance.logger

            log.debug("%s.%s Started", class_name, func.__name__)
            try:
                result = func(*args, **kwargs)
                log.debug("%s.%s Ended", class_name, func.__name__)
                return result
            except Exception as e:
                log.error("%s.%s Failed: %s", class_name, func.__name__, str(e), exc_info=True)
                raise
        return wrapper

    @staticmethod
    def info(msg, logger_instance=None):
        """Log info. Uses provided logger or default."""
        log = logger_instance or default_logger
        log.info(msg)

    @staticmethod
    def warning(msg, logger_instance=None):
        """Log warning. Uses provided logger or default."""
        log = logger_instance or default_logger
        log.warning(msg)

    warn = warning

    @staticmethod
    def error(msg, exc_info=True, logger_instance=None):
        """Log error. Uses provided logger or default."""
        log = logger_instance or default_logger
        log.error(msg, exc_info=exc_info)

    @staticmethod
    def debug(msg, logger_instance=None):
        """Log debug. Uses provided logger or default."""
        log = logger_instance or default_logger
        log.debug(msg)

import logging
import logging.config
import functools
import logging.handlers
import re
from ..configurations.api.config import BaseConfig
from ..configurations.api.config import LogConfig
from logging.handlers import TimedRotatingFileHandler
import os


def custom_namer(cls, default_name):
    base_filename, ext, date = default_name.split(".")
    return f"{base_filename}.{date}.{ext}"


class SensitiveDataFilter(logging.Filter):
    """
    Filter to mask sensitive fields like passwords, tokens, and secrets
    in both string and dictionary log messages.
    """
    SENSITIVE_KEYS = ['password', 'token', 'secret','username']

    def filter(self, record):
        def mask_dict(d):
            """Recursively mask sensitive values in dictionaries."""
            masked = {}
            for key, value in d.items():
                if isinstance(value, dict):
                    masked[key] = mask_dict(value)
                elif key.lower() in self.SENSITIVE_KEYS:
                    masked[key] = '****'
                else:
                    masked[key] = value
            return masked

        try:
            # Mask arguments passed as a dictionary
            if isinstance(record.args, dict):
                record.args = mask_dict(record.args)

            # Mask if the message itself is a dictionary
            if isinstance(record.msg, dict):
                record.msg = mask_dict(record.msg)

            # Mask if the message is a string containing sensitive patterns
            elif isinstance(record.msg, str):
                for key in self.SENSITIVE_KEYS:
                    record.msg = re.sub(
                        rf'(["\']?{key}["\']?\s*[:=]\s*[\'"])[^\'"]+([\'"])',
                        rf'\1****\2',
                        record.msg,
                        flags=re.IGNORECASE
                    )
        except Exception:
            # Fail silently to avoid breaking logging
            pass

        return True


class LoggerConfig:  # pragma: no cover
    """
    Logger configuration class to set up logging based on configuration file.

    This class reads a logging configuration file, adjusts the logging setup 
    according to the specified log level, and configures log handlers for 
    different log levels.
    """

    @staticmethod
    def setup_logging():
        """
        Set up logging configuration from the LogConfig.

        This method reads the logging configuration from a file, creates the 
        necessary log directories, adjusts the log handlers based on the 
        log level, and returns a configured logger.

        Returns:
            logging.Logger: Configured logger instance.
        """
        config = LogConfig.config

        # Apply initial logging configuration
        log_level = config["logger_type"]["level"]
        log_path = config["log_path"]["log_path"]

        if not os.path.exists(log_path):
            os.makedirs(log_path)

        # Replace placeholders in config with actual log path
        for section in config.sections():
            for key, value in config.items(section):
                if '%(log_path)s' in value:
                    new_value = value.replace('%(log_path)s', log_path)
                    config.set(section, key, new_value)

        # Configure logging from the file initially to set up basic config
        logging.config.fileConfig(config)

        logger_instance = logging.getLogger('openDataPipelineLogger')

        # Add sensitive data masking filter
        logger_instance.addFilter(SensitiveDataFilter())

        return logger_instance


# Initialize the logger
logger = LoggerConfig.setup_logging()

class Logger:  # pragma: no cover
    """
    Logger utility class for logging function start and end, as well as 
    info and error messages.
    """

    @staticmethod
    def generate(func):
        """
        Decorator to log the start and end of a function call.

        Args:
            func (function): The function to be decorated.

        Returns:
            function: The wrapped function with logging.
        """
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            class_name = args[0].__class__.__name__
            logger.debug("%s.%s Started", class_name, func.__name__)
            result = func(*args, **kwargs)
            logger.debug("%s.%s Ended", class_name, func.__name__)
            return result
        return wrapper

    @staticmethod
    def info(*msg):
        """
        Log an info message.

        Args:
            *msg: The message to log.
        """
        logger.info(" ".join(map(str, msg)))

    @staticmethod
    def warning(*msg):
        """Log a warning message."""
        logger.warning(" ".join(map(str, msg)))

    # convenience alias 
    warn = warning

    @staticmethod
    def error(*msg):
        """
        Log an error message.

        Args:
            *msg: The message to log.
        """
        logger.error(" ".join(map(str, msg)), exc_info=True)



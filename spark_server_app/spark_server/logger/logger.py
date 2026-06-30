import logging 
import logging.config
import functools
import re


class SensitiveDataFilter(logging.Filter):
    """
    Filter to mask sensitive fields like passwords, tokens, and secrets,username
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
            if isinstance(record.args, dict):
                record.args = mask_dict(record.args)

            if isinstance(record.msg, dict):
                record.msg = mask_dict(record.msg)

            elif isinstance(record.msg, str):
                for key in self.SENSITIVE_KEYS:
                    record.msg = re.sub(
                        rf'(["\']?{key}["\']?\s*[:=]\s*[\'"])[^\'"]+([\'"])',
                        rf'\1****\2',
                        record.msg,
                        flags=re.IGNORECASE
                    )
        except Exception:
            pass

        return True

# Configure the logging format and handlers
logging.basicConfig(
    format='%(asctime)s-%(msecs)03d %(levelname)-8s [%(pathname)s:%(lineno)d:%(funcName)s] %(message)s',
    handlers=[
        logging.FileHandler("app.log"),
        logging.StreamHandler()
    ]
)

# Create a logger object
logger = logging.getLogger(__name__)

logger.addFilter(SensitiveDataFilter())  

def set_logging_level(level):
    """
    Set the logging level dynamically based on user input.
    """
    numeric_level = getattr(logging, level.upper(), None)
    if not isinstance(numeric_level, int):
        raise ValueError(f'Invalid log level: {level}')
    logger.setLevel(numeric_level)
    for handler in logger.handlers:
        handler.setLevel(numeric_level)

class Logger:

    def generate(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            class_name = args[0].__class__.__name__
            logger.info("%s.%s Started", class_name, func.__name__)
            result = func(*args, **kwargs)
            logger.info("%s.%s Ended", class_name, func.__name__)
            return result
        return wrapper

    @staticmethod
    def info(*msg):
        logger.info(" ".join(map(str, msg)))

    @staticmethod
    def debug(*msg):
        logger.debug(" ".join(map(str, msg)))

    @staticmethod
    def warning(*msg):
        logger.warning(" ".join(map(str, msg)))
        
    @staticmethod
    def error(*msg):
        logger.error(" ".join(map(str, msg)))

import logging
from logging.config import dictConfig


LOGGING_CONFIG = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "default": {
            "format": "%(levelname)s | %(asctime)s | %(name)s | %(message)s",
        },
    },
    "handlers": {
        "default": {
            "class": "logging.StreamHandler",
            "formatter": "default",
            "level": "INFO",
        },
    },
    "root": {
        "level": "INFO",
        "handlers": ["default"],
    },
}


def configure_logging() -> None:
    """Configure application-wide logging."""

    dictConfig(LOGGING_CONFIG)
    logging.getLogger("uvicorn.access").setLevel(logging.WARNING)

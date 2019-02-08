import logging.config
import os
import sys

LOGGING_CONFIG_DEFAULTS = dict(
    version=1,
    disable_existing_loggers=False,

    loggers={
        "root": {
            "level": "DEBUG",
            "handlers": ["root"]
        }
    },
    handlers={
        "root": {
            "class": "logging.StreamHandler",
            "formatter": "generic",
            "stream": sys.stdout
        }
    },
    formatters={
        "generic": {
            "format": "%(asctime)s [%(process)d] [%(levelname)s] [%(filename)s] [%(lineno)d] %(message)s",
            "datefmt": "[%Y-%m-%d %H:%M:%S %z]",
            "class": "logging.Formatter"
        }
    }
)

root_logger = logging.getLogger('root')
logging.config.dictConfig(LOGGING_CONFIG_DEFAULTS)


def set_logger_config(config: dict):
    logging.config.dictConfig(config)

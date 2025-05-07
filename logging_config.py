import logging
import logging.config

# Define the logging configuration
LOGGING_CONFIG = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "default": {
            "format": "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        },
        "detailed": {
            "format": (
                "%(asctime)s - %(name)s - %(levelname)s - %(message)s "
                "[%(filename)s:%(lineno)d]"
            ),
        },
    },
    "handlers": {
        "console": {
            "class": "logging.StreamHandler",
            "formatter": "default",
        },
        "file": {
            "class": "logging.FileHandler",
            "filename": "lehlah_expand.log",  # Log file in the root directory
            "formatter": "detailed",
        },
    },
    "loggers": {
        "lehlah-expand": {
            "handlers": ["console", "file"],
            "level": "INFO",  # Change to DEBUG for more detailed logs
            "propagate": False,
        },
    },
}

# Apply the logging configuration
logging.config.dictConfig(LOGGING_CONFIG)

# Get the logger for the project
logger = logging.getLogger("lehlah-expand")
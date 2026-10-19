import logging
import logging.config


class ColorFormatter(logging.Formatter):
    RESET = "\033[0m"
    CYAN = "\033[36;1m"

    LEVEL_COLORS = {
        logging.DEBUG: "\033[34m",
        logging.INFO : "\033[32m",
        logging.WARNING: "\033[33m",
        logging.ERROR: "\033[31m",
        logging.CRITICAL: "\033[1;31m",
    }
    def format(self, record: logging.LogRecord) -> str:
        level_color = self.LEVEL_COLORS.get(record.levelno, "")
        time = self.formatTime(record, self.datefmt)
        message = record.getMessage()

        output = (
            f"{time} | "
            f"{level_color}{record.levelname:<8}{self.RESET} | "
            f"{self.CYAN}{record.name}:{record.funcName}{self.RESET}"
            f" - {message}"
        )

        if record.exc_info:
            if not record.exc_text:
                record.exc_text = self.formatException(record.exc_info)
            output += f"\n{level_color}{record.exc_text}{self.RESET}"

        return output



LOGGING_CONFIG = {
    "version": 1,
    "disable_existing_loggers": False,

    "formatters": {
        "standard": {
            "format": "%(asctime)s | %(levelname)-8s | %(name)s:%(funcName)s - %(message)s",
        },
        "color": {
            "()": ColorFormatter,
        }
    },

    "handlers": {
        "cmd": {
            "class": "logging.StreamHandler",
            "formatter": "color",
            "level": "DEBUG",
        },
        "file": {
            "class": "logging.handlers.RotatingFileHandler",
            "formatter": "standard",
            "level": "DEBUG",
            "filename": f"{__name__}.log",
            "maxBytes": 1 * 1024 * 1024,
            "backupCount": 3,
            "encoding": "utf-8",
        }
    },

    "root": {
        "level": "INFO",
        "handlers": ["cmd", "file"],
    },

    "loggers": {
        "notifier": {
            "level": "DEBUG",
            "propagate": True,
        },
        "telegram_bot": {
            "level": "DEBUG",
            "propagate": True,
        }
    }
}

def configure_logging() -> None:
    logging.config.dictConfig(LOGGING_CONFIG)
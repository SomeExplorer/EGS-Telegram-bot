import logging
import sys

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

file_handler = logging.FileHandler(f"{__name__}.log")
stdout_handler = logging.StreamHandler(sys.stdout)

file_formatter = logging.Formatter(
    fmt="%(name)s | %(asctime)s | %(levelname)s | %(message)s",
    datefmt="%d-%m-%Y %H:%M:%S"
)

stdout_formatter = logging.Formatter(
    fmt="%(name)s | %(asctime)s | %(levelname)s | %(message)s",
    datefmt="%d-%m-%Y %H:%M:%S"
)

file_handler.setFormatter(file_formatter)
stdout_handler.setFormatter(stdout_formatter)

logger.addHandler(file_handler)
logger.addHandler(stdout_handler)

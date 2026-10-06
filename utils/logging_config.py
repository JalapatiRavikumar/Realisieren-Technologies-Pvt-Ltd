"""
Logging configuration for the web scraping pipeline.

Configures both console and file handlers with structured, readable formats.
Logs are written to logs/scraper.log with UTF-8 encoding.
"""

import logging
import sys
from pathlib import Path

from config import CONFIG


def setup_logger(
    name: str = "scraper_pipeline",
    log_file: Path | None = None,
    level: int = logging.INFO,
    console_output: bool = True,
) -> logging.Logger:
    """
    Set up and return a configured logger instance.

    Args:
        name: Logger name.
        log_file: Destination path for log file. Defaults to CONFIG.LOG_FILE_PATH.
        level: Logging level (default: logging.INFO).
        console_output: Whether to attach a console StreamHandler.

    Returns:
        Configured logging.Logger instance.
    """
    logger = logging.getLogger(name)
    logger.setLevel(level)

    # Avoid duplicate handlers if already configured
    if logger.hasHandlers():
        return logger

    formatter = logging.Formatter(
        fmt="[%(asctime)s] [%(levelname)-8s] [%(name)s] %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )

    # File handler
    target_log_file = log_file or CONFIG.LOG_FILE_PATH
    target_log_file.parent.mkdir(parents=True, exist_ok=True)

    file_handler = logging.FileHandler(target_log_file, encoding="utf-8")
    file_handler.setLevel(level)
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)

    # Console handler
    if console_output:
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(level)
        console_handler.setFormatter(formatter)
        logger.addHandler(console_handler)

    return logger

"""Logging stub."""

import logging

logger = logging.getLogger("vibeshop")


def log_request(path: str) -> None:
    logger.info("request %s", path)

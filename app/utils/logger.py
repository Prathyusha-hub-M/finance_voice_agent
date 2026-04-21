import logging
import sys
from typing import Any, Dict, Optional


def setup_logger(name: str = "finance_agent") -> logging.Logger:
    logger = logging.getLogger(name)

    if logger.handlers:
        return logger  # prevent duplicate logs

    logger.setLevel(logging.INFO)

    handler = logging.StreamHandler(sys.stdout)
    formatter = logging.Formatter(
        fmt="%(asctime)s | %(levelname)s | %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S"
    )

    handler.setFormatter(formatter)
    logger.addHandler(handler)

    return logger


logger = setup_logger()


def log_event(
    state: Any,
    step: str,
    message: str,
    data: Optional[Dict[str, Any]] = None,
    level: str = "info"
):
    """
    State-based structured logging for LangGraph nodes.

    Usage:
        log_event(state, "validate", "start")
    """

    log_payload = {
        "request_id": getattr(state, "request_id", None),
        "step": step,
        "message": message,
        "data": data or {},
        "execution_path": getattr(state, "execution_path", [])
    }

    log_message = str(log_payload)

    if level == "error":
        logger.error(log_message)
    elif level == "warning":
        logger.warning(log_message)
    else:
        logger.info(log_message)
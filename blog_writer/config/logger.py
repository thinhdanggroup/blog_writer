import contextvars
import logging
import os

request_id_context = contextvars.ContextVar("request_id")

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
handler = logging.StreamHandler()

format_mode = os.getenv("LOG_FORMAT", "line")
line_formatter = logging.Formatter(
    fmt=" %(filename)-20s :: %(levelname)-6s :: %(lineno)-6s :: %(message)s"
)
handler.setFormatter(line_formatter)
logger.addHandler(handler)

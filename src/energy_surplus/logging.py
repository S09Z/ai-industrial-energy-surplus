"""JSON-line logs on stderr; command results remain machine-readable on stdout."""

import json
import logging
import sys
from datetime import UTC, datetime


class JsonFormatter(logging.Formatter):
    def format(self, record: logging.LogRecord) -> str:
        return json.dumps(
            {
                "timestamp": datetime.now(UTC).isoformat(),
                "level": record.levelname,
                "event": record.getMessage(),
                "run_id": getattr(record, "run_id", None),
                "details": getattr(record, "details", None),
            }
        )


def configure_logging() -> logging.Logger:
    logger = logging.getLogger("energy_surplus")
    handler = logging.StreamHandler(sys.stderr)
    handler.setFormatter(JsonFormatter())
    logger.handlers = [handler]
    logger.propagate = False
    logger.setLevel(logging.INFO)
    return logger

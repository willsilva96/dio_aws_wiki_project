import logging
import json

class CloudWatchJsonFormatter(logging.Formatter):
    def format(self, record):
        log_record = {
            "timestamp": self.formatTime(record, self.datefmt),
            "level": record.levelname,
            "logger": record.name,
            "service": getattr(record, "service", "SYSTEM"),
            "status": getattr(record, "status","INFO"),
            "document": getattr(record, "document", None),
            "message": record.getMessage()
        }

        if record.exc_info:
            log_record["exception"] = self.formatException(record.exc_info)

        return json.dumps(log_record, ensure_ascii=False, default=str)

def process_logger(
        name: str = "WikiDocumentProcess"
) -> logging.Logger:
    logger = logging.getLogger(name)
    logger.setLevel(logging.INFO)

    if not logger.handlers:
        ch = logging.StreamHandler()
        ch.setFormatter(CloudWatchJsonFormatter())
        logger.addHandler(ch)

    return logger
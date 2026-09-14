import logging
import json
from typing import Optional
from datetime import datetime, timezone

class CloudWatchJsonFormatter(logging.Formatter):
    def format(self, record):
        log_record = {
            "timestamp": self.formatTime(record, self.datefmt),
            "trace_id": getattr(record, "trace_id", "N/A"),
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

class S3MemoryLogHandler(logging.Handler):
    def __init__(
        self,
        s3_client,
        bucket_name: str,
        prefix: str = "audit_logs"):

        super().__init__()
        self.s3_client = s3_client
        self.bucket_name = bucket_name
        self.prefix = prefix
        self.buffer = []

    def emit(self, record):
        msg = self.format(record)
        self.buffer.append(msg)

    def flush_to_s3(self) -> bool:
        if not self.buffer or not self.s3_client:
            return False

        log_context = "\n".join(self.buffer)
        today_date = datetime.now(timezone.utc).strftime("%Y=%m-%d")
        hour_now = datetime.now(timezone.utc).strftime("%H%M%S")
        s3_key = f"{self.prefix}/{today_date}/pipeline_{hour_now}.log"

        try:
            self.s3_client.put_object(
                Bucket=self.bucket_name,
                Key=s3_key,
                Body=log_context.encode("utf-8"),
                ContentType="application/json"
            )

            print(f"\n [AUDIT] Logs send to s3://{self.bucket_name}/{s3_key}")

            self.buffer.clear()
            return True

        except Exception as e:
            print(f"[ERROR S3 Log] Message: {e}")
            return False

def process_logger(
        name: str = "WikiDocumentProcess",
        s3_client = None,
        bucket_logs: Optional[str] = None
) -> logging.Logger:

    logger = logging.getLogger(name)
    logger.setLevel(logging.INFO)
    formatter = CloudWatchJsonFormatter()

    if not logger.handlers:
        stream_handler = logging.StreamHandler()
        stream_handler.setFormatter(formatter)
        logger.addHandler(stream_handler)

    if s3_client and bucket_logs:
        s3_handler = S3MemoryLogHandler(
            s3_client=s3_client,
            bucket_name=bucket_logs,
        )
        s3_handler.setFormatter(formatter)
        logger.addHandler(s3_handler)

    return logger
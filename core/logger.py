import json
import logging
from datetime import datetime
from pathlib import Path


class StructuredAuditLogger:
    def __init__(self, log_dir: Path):
        self.log_dir = log_dir
        self.log_dir.mkdir(parents=True, exist_ok=True)
        self.audit_file = self.log_dir / "audit_trail.jsonl"
        self.logger = logging.getLogger("AIDataAnalyst")
        self.logger.setLevel(logging.INFO)
        if not self.logger.handlers:
            ch = logging.StreamHandler()
            formatter = logging.Formatter(
                "[%(asctime)s] [%(levelname)s] %(name)s: %(message)s"
            )
            ch.setFormatter(formatter)
            self.logger.addHandler(ch)

    def log_event(self, agent: str, event_type: str, payload: dict):
        entry = {
            "timestamp": datetime.utcnow().isoformat(),
            "agent": agent,
            "event_type": event_type,
            "payload": payload,
        }
        self.logger.info(f"{agent} -> {event_type}")
        with open(self.audit_file, "a", encoding="utf-8") as f:
            f.write(json.dumps(entry, default=str) + "\n")

import json
import os
from datetime import datetime, timezone


class IngestionLogger:
    def __init__(self, base_dir: str = "../data/logs"):
        self.base_dir = os.path.abspath(base_dir)
        os.makedirs(self.base_dir, exist_ok=True)

    def _file_path(self) -> str:
        return os.path.join(self.base_dir, "ingestion_log.jsonl")

    def log_run(self, source_system: str, fetched_count: int, saved_count: int, status: str, error: str = ""):
        payload = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "source_system": source_system,
            "fetched_count": fetched_count,
            "saved_count": saved_count,
            "status": status,
            "error": error,
        }

        with open(self._file_path(), "a", encoding="utf-8") as f:
            f.write(json.dumps(payload, ensure_ascii=False) + "\n")

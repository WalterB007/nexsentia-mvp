import json
import os
from dataclasses import asdict
from typing import Iterable, List, Set
from datetime import datetime

from ..models.canonical import CanonicalSignal


class JsonlSignalRepository:
    def __init__(self, base_dir: str = "../data/raw"):
        self.base_dir = os.path.abspath(base_dir)
        os.makedirs(self.base_dir, exist_ok=True)

    def _file_path(self) -> str:
        return os.path.join(self.base_dir, "signals.jsonl")

    def _existing_ids(self) -> Set[str]:
        path = self._file_path()
        if not os.path.exists(path):
            return set()

        ids = set()
        with open(path, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                try:
                    row = json.loads(line)
                    if "signal_id" in row:
                        ids.add(row["signal_id"])
                except json.JSONDecodeError:
                    continue
        return ids

    def save_signals(self, signals: Iterable[CanonicalSignal]) -> int:
        path = self._file_path()
        existing_ids = self._existing_ids()
        count = 0

        with open(path, "a", encoding="utf-8") as f:
            for signal in signals:
                if signal.signal_id in existing_ids:
                    continue

                payload = asdict(signal)
                if isinstance(payload.get("event_timestamp"), datetime):
                    payload["event_timestamp"] = payload["event_timestamp"].isoformat()

                f.write(json.dumps(payload, ensure_ascii=False) + "\n")
                existing_ids.add(signal.signal_id)
                count += 1

        return count

    def load_all(self) -> List[dict]:
        path = self._file_path()
        if not os.path.exists(path):
            return []

        rows = []
        with open(path, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if line:
                    rows.append(json.loads(line))
        return rows

import json
import threading
from pathlib import Path
from typing import Any


class ResultStore:
    def __init__(self, data_file: Path):
        self._data_file = data_file
        self._lock = threading.Lock()
        self._data_file.parent.mkdir(parents=True, exist_ok=True)
        if not self._data_file.exists():
            self._data_file.write_text("[]", encoding="utf-8")

    def _read(self) -> list[dict[str, Any]]:
        try:
            return json.loads(self._data_file.read_text(encoding="utf-8") or "[]")
        except json.JSONDecodeError:
            return []

    def _write(self, records: list[dict[str, Any]]) -> None:
        self._data_file.write_text(json.dumps(records, indent=2), encoding="utf-8")

    def all(self) -> list[dict[str, Any]]:
        with self._lock:
            return self._read()

    def upsert(self, record: dict[str, Any]) -> dict[str, Any]:
        key = record.get("source_url")
        with self._lock:
            records = self._read()
            index = next((i for i, r in enumerate(records) if r.get("source_url") == key), None)
            if index is not None:
                records[index] = record
            else:
                records.append(record)
            self._write(records)
        return record

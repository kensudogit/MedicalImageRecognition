"""解析結果キャッシュ（コンテンツハッシュ）"""

from __future__ import annotations

import hashlib
import json
import threading
import time
from collections import OrderedDict
from pathlib import Path
from typing import Any, Optional

from app.models.schemas import DetectionResult


class AnalysisCache:
    def __init__(self, max_entries: int = 128, ttl_seconds: int = 3600) -> None:
        self.max_entries = max_entries
        self.ttl_seconds = ttl_seconds
        self._data: OrderedDict[str, tuple[float, dict[str, Any]]] = OrderedDict()
        self._lock = threading.Lock()
        self.hits = 0
        self.misses = 0

    @staticmethod
    def content_key(
        file_path: Path,
        modality: str,
        provider: str,
        model_version: str = "",
        generate_findings: bool = True,
    ) -> str:
        h = hashlib.sha256()
        with file_path.open("rb") as f:
            while True:
                chunk = f.read(1024 * 1024)
                if not chunk:
                    break
                h.update(chunk)
        h.update(f"|{modality}|{provider}|{model_version}|{generate_findings}".encode())
        return h.hexdigest()

    def get(self, key: str) -> Optional[DetectionResult]:
        with self._lock:
            item = self._data.get(key)
            if not item:
                self.misses += 1
                return None
            ts, payload = item
            if time.time() - ts > self.ttl_seconds:
                self._data.pop(key, None)
                self.misses += 1
                return None
            self._data.move_to_end(key)
            self.hits += 1
            return DetectionResult.model_validate(payload)

    def set(self, key: str, result: DetectionResult) -> None:
        with self._lock:
            self._data[key] = (time.time(), json.loads(result.model_dump_json()))
            self._data.move_to_end(key)
            while len(self._data) > self.max_entries:
                self._data.popitem(last=False)

    def stats(self) -> dict[str, Any]:
        total = self.hits + self.misses
        return {
            "hits": self.hits,
            "misses": self.misses,
            "hit_rate": (self.hits / total) if total else 0.0,
            "entries": len(self._data),
            "max_entries": self.max_entries,
            "ttl_seconds": self.ttl_seconds,
        }

    def clear(self) -> None:
        with self._lock:
            self._data.clear()
            self.hits = 0
            self.misses = 0


analysis_cache = AnalysisCache()

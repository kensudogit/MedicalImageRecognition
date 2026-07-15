"""自社AIモデルプロバイダー（ローカルCVエンジン優先）"""

import asyncio
import time
from pathlib import Path
from typing import Optional

import httpx

from app.config import settings
from app.models.schemas import (
    AiProvider,
    AnalyzeRequest,
    BoundingBox,
    ClassificationResult,
    DetectionResult,
    Modality,
)
from app.providers.base import BaseImagingProvider
from app.services.local_cv_engine import analyze_image_file


class InHouseProvider(BaseImagingProvider):
    provider = AiProvider.INHOUSE

    async def is_available(self) -> bool:
        # ローカルCVは常に利用可能
        if settings.use_local_cv:
            return True
        if not settings.inhouse_model_url:
            return settings.use_local_cv
        try:
            async with httpx.AsyncClient(timeout=3.0) as client:
                r = await client.get(f"{settings.inhouse_model_url.rstrip('/')}/health")
                return r.status_code < 500
        except Exception:
            return settings.use_local_cv

    async def analyze(
        self,
        image_path: Path,
        modality: Modality,
        request: AnalyzeRequest,
        preview_path: Optional[Path] = None,
    ) -> DetectionResult:
        start = time.perf_counter()

        # 1) リモート自社モデル（明示設定時）
        if (
            settings.inhouse_model_url
            and settings.inhouse_api_key
            and not settings.force_local_cv
        ):
            try:
                return await self._remote_analyze(
                    image_path, modality, request, start
                )
            except Exception:
                if not settings.use_local_cv:
                    raise

        # 2) ローカル画素ベースCV（実用デフォルト）
        if settings.use_local_cv:
            return await asyncio.to_thread(
                analyze_image_file,
                image_path,
                modality,
                preview_path,
                AiProvider.INHOUSE,
            )

        raise RuntimeError("利用可能な自社推論エンジンがありません")

    async def _remote_analyze(
        self,
        image_path: Path,
        modality: Modality,
        request: AnalyzeRequest,
        start: float,
    ) -> DetectionResult:
        headers = {"Authorization": f"Bearer {settings.inhouse_api_key}"}
        async with httpx.AsyncClient(timeout=60.0) as client:
            with image_path.open("rb") as f:
                files = {"file": (image_path.name, f, "application/octet-stream")}
                data = {
                    "modality": modality.value,
                    "generate_findings": str(request.generate_findings).lower(),
                }
                response = await client.post(
                    settings.inhouse_model_url,
                    headers=headers,
                    files=files,
                    data=data,
                )
                response.raise_for_status()
                payload = response.json()

        boxes = [BoundingBox(**b) for b in payload.get("boxes", [])]
        classifications = [
            ClassificationResult(**c) for c in payload.get("classifications", [])
        ]
        return DetectionResult(
            boxes=boxes,
            classifications=classifications,
            findings_text=payload.get("findings_text", ""),
            provider=AiProvider.INHOUSE,
            modality=modality,
            model_version=payload.get("model_version", "inhouse-remote"),
            processing_ms=int((time.perf_counter() - start) * 1000),
            raw=payload,
        )

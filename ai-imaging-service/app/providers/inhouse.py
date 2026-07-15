"""自社AIモデルプロバイダー"""

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
from app.providers.mock_results import build_mock_result


class InHouseProvider(BaseImagingProvider):
    provider = AiProvider.INHOUSE

    async def is_available(self) -> bool:
        if settings.enable_mock_inference and not settings.inhouse_model_url:
            return True
        if not settings.inhouse_model_url:
            return False
        try:
            async with httpx.AsyncClient(timeout=3.0) as client:
                r = await client.get(f"{settings.inhouse_model_url.rstrip('/')}/health")
                return r.status_code < 500
        except Exception:
            return settings.enable_mock_inference

    async def analyze(
        self,
        image_path: Path,
        modality: Modality,
        request: AnalyzeRequest,
        preview_path: Optional[Path] = None,
    ) -> DetectionResult:
        start = time.perf_counter()

        if settings.enable_mock_inference or not settings.inhouse_api_key:
            result = build_mock_result(modality, AiProvider.INHOUSE, "inhouse-v1")
            result.processing_ms = int((time.perf_counter() - start) * 1000)
            return result

        headers = {}
        if settings.inhouse_api_key:
            headers["Authorization"] = f"Bearer {settings.inhouse_api_key}"

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
            model_version=payload.get("model_version", "inhouse-v1"),
            processing_ms=int((time.perf_counter() - start) * 1000),
            raw=payload,
        )
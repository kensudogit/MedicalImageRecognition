"""外部医療AI API プロバイダー"""

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


class ExternalMedicalAiProvider(BaseImagingProvider):
    provider = AiProvider.EXTERNAL

    async def is_available(self) -> bool:
        if settings.external_medical_ai_url:
            return True
        return settings.enable_mock_inference

    async def analyze(
        self,
        image_path: Path,
        modality: Modality,
        request: AnalyzeRequest,
        preview_path: Optional[Path] = None,
    ) -> DetectionResult:
        start = time.perf_counter()

        if not settings.external_medical_ai_url or settings.enable_mock_inference:
            result = build_mock_result(modality, AiProvider.EXTERNAL, "external-mock")
            result.processing_ms = int((time.perf_counter() - start) * 1000)
            return result

        headers = {"Accept": "application/json"}
        if settings.external_medical_ai_key:
            headers["Authorization"] = f"Bearer {settings.external_medical_ai_key}"

        async with httpx.AsyncClient(timeout=90.0) as client:
            with image_path.open("rb") as f:
                files = {"file": (image_path.name, f, "application/octet-stream")}
                data = {
                    "modality": modality.value,
                    "generate_findings": str(request.generate_findings).lower(),
                }
                if request.patient_context:
                    data["patient_context"] = request.patient_context
                response = await client.post(
                    settings.external_medical_ai_url,
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
            provider=AiProvider.EXTERNAL,
            modality=modality,
            model_version=payload.get("model_version", "external-api"),
            processing_ms=int((time.perf_counter() - start) * 1000),
            raw=payload,
        )
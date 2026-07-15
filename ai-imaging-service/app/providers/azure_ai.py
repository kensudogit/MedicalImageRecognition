"""Azure AI プロバイダー"""

import base64
import time
from pathlib import Path
from typing import Optional

import httpx

from app.config import settings
from app.models.schemas import AiProvider, AnalyzeRequest, DetectionResult, Modality
from app.providers.base import BaseImagingProvider
from app.providers.mock_results import build_mock_result


class AzureAiProvider(BaseImagingProvider):
    provider = AiProvider.AZURE

    async def is_available(self) -> bool:
        if settings.azure_ai_endpoint and settings.azure_ai_key:
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

        if not settings.azure_ai_endpoint or settings.enable_mock_inference:
            result = build_mock_result(modality, AiProvider.AZURE, "azure-mock")
            result.processing_ms = int((time.perf_counter() - start) * 1000)
            return result

        encoded = base64.b64encode(image_path.read_bytes()).decode("utf-8")
        headers = {
            "api-key": settings.azure_ai_key,
            "Content-Type": "application/json",
        }
        payload = {
            "model": settings.azure_ai_model,
            "modality": modality.value,
            "image_base64": encoded,
            "generate_findings": request.generate_findings,
        }
        async with httpx.AsyncClient(timeout=90.0) as client:
            response = await client.post(
                settings.azure_ai_endpoint.rstrip("/") + "/analyze",
                headers=headers,
                json=payload,
            )
            response.raise_for_status()
            data = response.json()

        result = build_mock_result(modality, AiProvider.AZURE, "azure-ai")
        result.raw = data
        result.findings_text = data.get("findings_text", result.findings_text)
        result.processing_ms = int((time.perf_counter() - start) * 1000)
        return result

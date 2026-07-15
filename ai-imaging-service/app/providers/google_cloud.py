"""Google Cloud AI プロバイダー"""

import time
from pathlib import Path
from typing import Optional

from app.config import settings
from app.models.schemas import AiProvider, AnalyzeRequest, DetectionResult, Modality
from app.providers.base import BaseImagingProvider
from app.providers.mock_results import build_mock_result


class GoogleCloudProvider(BaseImagingProvider):
    provider = AiProvider.GOOGLE

    async def is_available(self) -> bool:
        if settings.gcp_project_id and settings.gcp_endpoint_id:
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

        if not settings.gcp_endpoint_id or settings.enable_mock_inference:
            result = build_mock_result(modality, AiProvider.GOOGLE, "gcp-mock")
            result.processing_ms = int((time.perf_counter() - start) * 1000)
            return result

        # Vertex AI endpoint 呼び出し（実エンドポイント接続時）
        try:
            from google.cloud import aiplatform

            aiplatform.init(
                project=settings.gcp_project_id,
                location=settings.gcp_location,
            )
            endpoint = aiplatform.Endpoint(settings.gcp_endpoint_id)
            instances = [
                {
                    "content": image_path.read_bytes().hex(),
                    "modality": modality.value,
                }
            ]
            prediction = endpoint.predict(instances=instances)
            raw = {"predictions": [str(p) for p in prediction.predictions]}
        except Exception as exc:
            raw = {"error": str(exc)}

        result = build_mock_result(modality, AiProvider.GOOGLE, "vertex-ai")
        result.raw = raw
        result.processing_ms = int((time.perf_counter() - start) * 1000)
        return result

"""AWS SageMaker プロバイダー"""

import json
import time
from pathlib import Path
from typing import Optional

from app.config import settings
from app.models.schemas import AiProvider, AnalyzeRequest, DetectionResult, Modality
from app.providers.base import BaseImagingProvider
from app.providers.mock_results import build_mock_result


class SageMakerProvider(BaseImagingProvider):
    provider = AiProvider.SAGEMAKER

    async def is_available(self) -> bool:
        if settings.sagemaker_endpoint_name and settings.aws_region:
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

        if not settings.sagemaker_endpoint_name or settings.enable_mock_inference:
            result = build_mock_result(modality, AiProvider.SAGEMAKER, "sagemaker-mock")
            result.processing_ms = int((time.perf_counter() - start) * 1000)
            return result

        import boto3

        runtime = boto3.client(
            "sagemaker-runtime",
            region_name=settings.aws_region,
            aws_access_key_id=settings.aws_access_key_id or None,
            aws_secret_access_key=settings.aws_secret_access_key or None,
        )
        body = image_path.read_bytes()
        response = runtime.invoke_endpoint(
            EndpointName=settings.sagemaker_endpoint_name,
            ContentType="application/octet-stream",
            Body=body,
            CustomAttributes=json.dumps({"modality": modality.value}),
        )
        payload = json.loads(response["Body"].read().decode("utf-8"))
        result = build_mock_result(modality, AiProvider.SAGEMAKER, "sagemaker-endpoint")
        result.raw = payload
        result.findings_text = payload.get("findings_text", result.findings_text)
        result.processing_ms = int((time.perf_counter() - start) * 1000)
        return result

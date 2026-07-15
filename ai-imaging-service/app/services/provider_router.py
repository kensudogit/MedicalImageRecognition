"""所見文章生成・プロバイダールーター"""

from pathlib import Path
from typing import Optional

from app.config import settings
from app.models.schemas import AiProvider, AnalyzeRequest, DetectionResult, Modality
from app.providers.azure_ai import AzureAiProvider
from app.providers.base import BaseImagingProvider
from app.providers.external_medical import ExternalMedicalAiProvider
from app.providers.google_cloud import GoogleCloudProvider
from app.providers.inhouse import InHouseProvider
from app.providers.sagemaker import SageMakerProvider


class ProviderRouter:
    def __init__(self) -> None:
        self._providers: dict[AiProvider, BaseImagingProvider] = {
            AiProvider.INHOUSE: InHouseProvider(),
            AiProvider.SAGEMAKER: SageMakerProvider(),
            AiProvider.AZURE: AzureAiProvider(),
            AiProvider.GOOGLE: GoogleCloudProvider(),
            AiProvider.EXTERNAL: ExternalMedicalAiProvider(),
        }

    def get(self, provider: Optional[AiProvider] = None) -> BaseImagingProvider:
        key = provider or AiProvider(settings.default_provider)
        return self._providers[key]

    def all_providers(self) -> dict[AiProvider, BaseImagingProvider]:
        return self._providers

    async def availability_map(self) -> dict[str, bool]:
        result = {}
        for key, provider in self._providers.items():
            result[key.value] = await provider.is_available()
        return result

    async def analyze(
        self,
        image_path: Path,
        modality: Modality,
        request: AnalyzeRequest,
        preview_path: Optional[Path] = None,
    ) -> DetectionResult:
        provider = self.get(request.provider)
        result = await provider.analyze(image_path, modality, request, preview_path)
        if request.generate_findings and not result.findings_text:
            result.findings_text = enrich_findings(result, request.patient_context)
        elif request.patient_context and result.findings_text:
            result.findings_text = (
                f"{result.findings_text}\n\n【臨床情報】{request.patient_context}"
            )
        return result


def enrich_findings(result: DetectionResult, patient_context: Optional[str]) -> str:
    labels = [b.label for b in result.boxes]
    classes = [c.label for c in result.classifications]
    parts = [
        f"モダリティ: {result.modality.value}",
        f"プロバイダー: {result.provider.value}",
    ]
    if labels:
        parts.append(f"検出病変候補: {', '.join(labels)}")
    if classes:
        parts.append(f"分類: {', '.join(classes)}")
    if patient_context:
        parts.append(f"臨床情報: {patient_context}")
    parts.append("本結果は支援情報であり、最終診断は医師が行ってください。")
    return "\n".join(parts)


provider_router = ProviderRouter()

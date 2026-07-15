"""所見文章生成・プロバイダールーター（キャッシュ・並列制御付き）"""

import asyncio
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
from app.services.cache import analysis_cache


class ProviderRouter:
    def __init__(self) -> None:
        self._providers: dict[AiProvider, BaseImagingProvider] = {
            AiProvider.INHOUSE: InHouseProvider(),
            AiProvider.SAGEMAKER: SageMakerProvider(),
            AiProvider.AZURE: AzureAiProvider(),
            AiProvider.GOOGLE: GoogleCloudProvider(),
            AiProvider.EXTERNAL: ExternalMedicalAiProvider(),
        }
        self._semaphore = asyncio.Semaphore(settings.max_concurrent_analyses)
        analysis_cache.max_entries = settings.cache_max_entries
        analysis_cache.ttl_seconds = settings.cache_ttl_seconds
        self.total_analyses = 0
        self.total_processing_ms = 0

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
        provider_key = (request.provider or AiProvider(settings.default_provider)).value
        cache_key = None
        if settings.cache_enabled:
            cache_key = analysis_cache.content_key(
                image_path,
                modality.value,
                provider_key,
                model_version="local-cv-1.1",
                generate_findings=request.generate_findings,
            )
            cached = analysis_cache.get(cache_key)
            if cached is not None:
                raw = dict(cached.raw or {})
                raw["cache_hit"] = True
                cached.raw = raw
                cached.processing_ms = 0
                return cached

        async with self._semaphore:
            provider = self.get(request.provider)
            result = await provider.analyze(
                image_path, modality, request, preview_path
            )

        if request.generate_findings and not result.findings_text:
            result.findings_text = enrich_findings(result, request.patient_context)
        elif request.patient_context and result.findings_text:
            result.findings_text = (
                f"{result.findings_text}\n\n【臨床情報】{request.patient_context}"
            )

        self.total_analyses += 1
        self.total_processing_ms += int(result.processing_ms or 0)

        if settings.cache_enabled and cache_key:
            raw = dict(result.raw or {})
            raw["cache_hit"] = False
            result.raw = raw
            analysis_cache.set(cache_key, result)

        return result

    def performance_stats(self) -> dict:
        avg = (
            self.total_processing_ms / self.total_analyses
            if self.total_analyses
            else 0.0
        )
        return {
            "total_analyses": self.total_analyses,
            "avg_processing_ms": round(avg, 2),
            "max_concurrent_analyses": settings.max_concurrent_analyses,
            "cache": analysis_cache.stats(),
            "use_local_cv": settings.use_local_cv,
            "default_provider": settings.default_provider,
        }


def enrich_findings(result: DetectionResult, patient_context: Optional[str]) -> str:
    labels = [b.label for b in result.boxes]
    classes = [c.label for c in result.classifications]
    parts = [
        f"モダリティ: {result.modality.value}",
        f"プロバイダー: {result.provider.value}",
        f"モデル: {result.model_version}",
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

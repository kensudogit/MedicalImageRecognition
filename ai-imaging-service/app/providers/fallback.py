"""未接続時の実用フォールバック（ローカルCV優先）"""

from __future__ import annotations

import asyncio
from pathlib import Path
from typing import Optional

from app.config import settings
from app.models.schemas import AiProvider, DetectionResult, Modality
from app.providers.mock_results import build_mock_result
from app.services.local_cv_engine import analyze_image_file


async def practical_fallback(
    image_path: Path,
    modality: Modality,
    provider: AiProvider,
    preview_path: Optional[Path] = None,
    mock_version: str = "legacy-mock",
) -> DetectionResult:
    """クラウド未接続時: ローカルCV → （明示時のみ）固定モック"""
    if settings.use_local_cv:
        result = await asyncio.to_thread(
            analyze_image_file,
            image_path,
            modality,
            preview_path,
            provider,
        )
        raw = dict(result.raw or {})
        raw["fallback"] = "local_cv"
        result.raw = raw
        return result

    if settings.enable_mock_inference:
        return build_mock_result(modality, provider, mock_version)

    raise RuntimeError(
        f"{provider.value}: エンドポイント未設定かつローカルCV/モック無効です"
    )

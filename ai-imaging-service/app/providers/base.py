"""画像認識プロバイダー基底クラス"""

from abc import ABC, abstractmethod
from pathlib import Path
from typing import Optional

from app.models.schemas import (
    AiProvider,
    AnalyzeRequest,
    DetectionResult,
    Modality,
)


class BaseImagingProvider(ABC):
    provider: AiProvider

    @abstractmethod
    async def is_available(self) -> bool:
        """プロバイダーが利用可能か"""

    @abstractmethod
    async def analyze(
        self,
        image_path: Path,
        modality: Modality,
        request: AnalyzeRequest,
        preview_path: Optional[Path] = None,
    ) -> DetectionResult:
        """画像解析を実行"""

    def name(self) -> str:
        return self.provider.value
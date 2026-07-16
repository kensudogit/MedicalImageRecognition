"""医療画像AIサービス設定"""

from __future__ import annotations

import os
from typing import Literal

from pydantic import model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_prefix="AI_",
        extra="ignore",
    )

    app_name: str = "Medical Imaging AI Service"
    app_version: str = "1.2.0"
    host: str = "0.0.0.0"
    port: int = 8090

    default_provider: Literal[
        "inhouse", "openai", "sagemaker", "azure", "google", "external"
    ] = "inhouse"

    # 自社モデル（リモート）
    inhouse_model_url: str = ""
    inhouse_api_key: str = ""

    # OpenAI Vision
    # Railway 等では OPENAI_API_KEY（プレフィックスなし）を優先参照
    openai_api_key: str = ""
    openai_model: str = "gpt-4o"
    openai_base_url: str = "https://api.openai.com/v1"
    openai_organization: str = ""
    openai_max_tokens: int = 1200
    openai_timeout_seconds: float = 90.0

    # ローカルCVエンジン（デフォルトON = 実用性能）
    use_local_cv: bool = True
    force_local_cv: bool = False

    # AWS SageMaker
    aws_region: str = "ap-northeast-1"
    sagemaker_endpoint_name: str = ""
    aws_access_key_id: str = ""
    aws_secret_access_key: str = ""

    # Azure AI
    azure_ai_endpoint: str = ""
    azure_ai_key: str = ""
    azure_ai_model: str = "medical-imaging"

    # Google Cloud
    gcp_project_id: str = ""
    gcp_location: str = "asia-northeast1"
    gcp_endpoint_id: str = ""

    # 外部医療AI API
    external_medical_ai_url: str = ""
    external_medical_ai_key: str = ""

    # ストレージ
    upload_dir: str = "./uploads/ai-imaging"
    preview_dir: str = "./uploads/ai-imaging/previews"

    # 後方互換: True でもローカルCVを使う（固定モックは使わない）
    enable_mock_inference: bool = False

    # 性能
    cache_enabled: bool = True
    cache_ttl_seconds: int = 3600
    cache_max_entries: int = 128
    max_concurrent_analyses: int = 4
    preview_max_size: int = 1024

    @model_validator(mode="after")
    def resolve_openai_from_railway(self) -> "Settings":
        """Railway の OPENAI_API_KEY 等（プレフィックスなし）を取り込む。

        AI_ プレフィックス設定だけでは OPENAI_API_KEY を読めないため、
        未設定時は標準の環境変数名をフォールバックする。
        """
        key = (self.openai_api_key or "").strip()
        if not key:
            key = (
                os.environ.get("OPENAI_API_KEY")
                or os.environ.get("AI_OPENAI_API_KEY")
                or ""
            ).strip()
            object.__setattr__(self, "openai_api_key", key)

        # OPENAI_MODEL（Railway）— AI_OPENAI_MODEL 未指定時のみ
        if not (os.environ.get("AI_OPENAI_MODEL") or "").strip():
            railway_model = (os.environ.get("OPENAI_MODEL") or "").strip()
            if railway_model:
                object.__setattr__(self, "openai_model", railway_model)

        org = (self.openai_organization or "").strip()
        if not org:
            org = (
                os.environ.get("OPENAI_ORGANIZATION")
                or os.environ.get("OPENAI_ORG_ID")
                or ""
            ).strip()
            if org:
                object.__setattr__(self, "openai_organization", org)

        if not (os.environ.get("AI_OPENAI_BASE_URL") or "").strip():
            railway_base = (os.environ.get("OPENAI_BASE_URL") or "").strip()
            if railway_base:
                object.__setattr__(self, "openai_base_url", railway_base)

        return self

    @property
    def openai_configured(self) -> bool:
        return bool((self.openai_api_key or "").strip())


settings = Settings()

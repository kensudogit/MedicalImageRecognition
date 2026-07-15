"""医療画像AIサービス設定"""

from pydantic_settings import BaseSettings
from typing import Literal


class Settings(BaseSettings):
    app_name: str = "Medical Imaging AI Service"
    app_version: str = "1.1.0"
    host: str = "0.0.0.0"
    port: int = 8090

    default_provider: Literal[
        "inhouse", "sagemaker", "azure", "google", "external"
    ] = "inhouse"

    # 自社モデル（リモート）
    inhouse_model_url: str = ""
    inhouse_api_key: str = ""

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

    class Config:
        env_file = ".env"
        env_prefix = "AI_"


settings = Settings()

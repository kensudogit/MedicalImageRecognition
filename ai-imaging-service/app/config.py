"""医療画像AIサービス設定"""

from pydantic_settings import BaseSettings
from typing import Literal


class Settings(BaseSettings):
    app_name: str = "Medical Imaging AI Service"
    app_version: str = "1.0.0"
    host: str = "0.0.0.0"
    port: int = 8090

    # デフォルト推論プロバイダー
    default_provider: Literal[
        "inhouse", "sagemaker", "azure", "google", "external"
    ] = "inhouse"

    # 自社モデル
    inhouse_model_url: str = "http://localhost:9000/predict"
    inhouse_api_key: str = ""

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

    # モック推論（実API未設定時）
    enable_mock_inference: bool = True

    class Config:
        env_file = ".env"
        env_prefix = "AI_"


settings = Settings()
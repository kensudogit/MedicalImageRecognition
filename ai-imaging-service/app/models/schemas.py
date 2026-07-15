"""リクエスト／レスポンススキーマ"""

from enum import Enum
from typing import Any, Optional
from pydantic import BaseModel, Field


class Modality(str, Enum):
    XRAY = "XRAY"
    CT = "CT"
    MRI = "MRI"
    ULTRASOUND = "ULTRASOUND"
    ENDOSCOPY = "ENDOSCOPY"
    PATHOLOGY = "PATHOLOGY"
    DICOM = "DICOM"
    OTHER = "OTHER"


class AiProvider(str, Enum):
    INHOUSE = "inhouse"
    SAGEMAKER = "sagemaker"
    AZURE = "azure"
    GOOGLE = "google"
    EXTERNAL = "external"


class BoundingBox(BaseModel):
    """検出枠（正規化座標 0.0–1.0）"""
    x: float = Field(..., ge=0.0, le=1.0, description="左上X")
    y: float = Field(..., ge=0.0, le=1.0, description="左上Y")
    width: float = Field(..., ge=0.0, le=1.0, description="幅")
    height: float = Field(..., ge=0.0, le=1.0, description="高さ")
    label: str = Field(..., description="病変ラベル")
    confidence: float = Field(..., ge=0.0, le=1.0, description="信頼度")
    finding_code: Optional[str] = None


class ClassificationResult(BaseModel):
    label: str
    confidence: float
    category: Optional[str] = None


class DetectionResult(BaseModel):
    boxes: list[BoundingBox] = []
    classifications: list[ClassificationResult] = []
    findings_text: str = ""
    provider: AiProvider
    modality: Modality
    model_version: str = "mock-1.0"
    processing_ms: int = 0
    raw: Optional[dict[str, Any]] = None


class AnalyzeRequest(BaseModel):
    modality: Optional[Modality] = None
    provider: Optional[AiProvider] = None
    generate_findings: bool = True
    patient_context: Optional[str] = None


class DicomMetadata(BaseModel):
    patient_id: Optional[str] = None
    patient_name: Optional[str] = None
    study_instance_uid: Optional[str] = None
    series_instance_uid: Optional[str] = None
    sop_instance_uid: Optional[str] = None
    modality: Optional[str] = None
    study_date: Optional[str] = None
    study_description: Optional[str] = None
    series_description: Optional[str] = None
    rows: Optional[int] = None
    columns: Optional[int] = None
    manufacturer: Optional[str] = None
    institution_name: Optional[str] = None


class HealthResponse(BaseModel):
    status: str
    version: str
    providers: dict[str, bool]
    default_provider: str
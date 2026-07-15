"""モック推論結果（実API未接続時のデモ用）"""

from app.models.schemas import (
    AiProvider,
    BoundingBox,
    ClassificationResult,
    DetectionResult,
    Modality,
)

_MODALITY_FINDINGS: dict[Modality, tuple[str, list[BoundingBox], list[ClassificationResult]]] = {
    Modality.XRAY: (
        "胸部X線写真において、右上肺野に淡い陰影を認めます。"
        "肺炎または浸潤影の可能性が考えられます。臨床所見との対比を推奨します。",
        [
            BoundingBox(
                x=0.55, y=0.22, width=0.18, height=0.15,
                label="浸潤影候補", confidence=0.86, finding_code="XR-INFILTRATE",
            ),
            BoundingBox(
                x=0.32, y=0.48, width=0.12, height=0.10,
                label="結節影候補", confidence=0.71, finding_code="XR-NODULE",
            ),
        ],
        [
            ClassificationResult(label="異常所見あり", confidence=0.84, category="abnormality"),
            ClassificationResult(label="肺炎疑い", confidence=0.72, category="diagnosis"),
        ],
    ),
    Modality.CT: (
        "胸部CTにおいて、右肺上葉にすりガラス影を認めます。"
        "悪性腫瘍の可能性も否定できず、精密検査を推奨します。",
        [
            BoundingBox(
                x=0.42, y=0.30, width=0.20, height=0.18,
                label="すりガラス影", confidence=0.91, finding_code="CT-GGO",
            ),
        ],
        [
            ClassificationResult(label="肺病変疑い", confidence=0.88, category="abnormality"),
            ClassificationResult(label="悪性の可能性", confidence=0.62, category="risk"),
        ],
    ),
    Modality.MRI: (
        "頭部MRI（T2強調）において、左大脳半球に高信号域を認めます。"
        "梗塞または脱髄病変の鑑別が必要です。",
        [
            BoundingBox(
                x=0.28, y=0.35, width=0.16, height=0.14,
                label="高信号域", confidence=0.79, finding_code="MRI-HYPER",
            ),
        ],
        [
            ClassificationResult(label="異常信号あり", confidence=0.80, category="abnormality"),
        ],
    ),
    Modality.ULTRASOUND: (
        "腹部超音波検査において、肝右葉に低エコー領域を認めます。"
        "嚢胞または腫瘤性病変の可能性があり、追加検査を推奨します。",
        [
            BoundingBox(
                x=0.40, y=0.40, width=0.15, height=0.15,
                label="低エコー領域", confidence=0.75, finding_code="US-HYPO",
            ),
        ],
        [
            ClassificationResult(label="肝病変候補", confidence=0.74, category="abnormality"),
        ],
    ),
    Modality.ENDOSCOPY: (
        "上部消化管内視鏡所見として、胃前庭部に発赤・びらんを認めます。"
        "胃炎または潰瘍性病変の可能性が考えられます。",
        [
            BoundingBox(
                x=0.35, y=0.38, width=0.25, height=0.20,
                label="発赤・びらん", confidence=0.83, finding_code="ES-EROSION",
            ),
        ],
        [
            ClassificationResult(label="胃炎疑い", confidence=0.81, category="diagnosis"),
        ],
    ),
    Modality.PATHOLOGY: (
        "病理組織画像において、異型細胞の集簇を認めます。"
        "悪性の可能性があり、病理医による最終診断が必要です。",
        [
            BoundingBox(
                x=0.30, y=0.28, width=0.35, height=0.30,
                label="異型細胞集簇", confidence=0.89, finding_code="PATH-ATYPIA",
            ),
        ],
        [
            ClassificationResult(label="悪性疑い", confidence=0.77, category="risk"),
        ],
    ),
    Modality.DICOM: (
        "DICOM画像の解析結果として、注目領域に病変候補を検出しました。"
        "画像モダリティに応じた専門医の確認を推奨します。",
        [
            BoundingBox(
                x=0.40, y=0.35, width=0.20, height=0.18,
                label="病変候補", confidence=0.78, finding_code="DICOM-LESION",
            ),
        ],
        [
            ClassificationResult(label="要精査", confidence=0.76, category="abnormality"),
        ],
    ),
    Modality.OTHER: (
        "画像解析により病変候補を検出しました。臨床所見との照合を推奨します。",
        [
            BoundingBox(
                x=0.38, y=0.38, width=0.22, height=0.20,
                label="異常領域", confidence=0.70, finding_code="GEN-ABNORMAL",
            ),
        ],
        [
            ClassificationResult(label="異常所見候補", confidence=0.70, category="abnormality"),
        ],
    ),
}


def build_mock_result(
    modality: Modality,
    provider: AiProvider,
    model_version: str,
) -> DetectionResult:
    findings, boxes, classifications = _MODALITY_FINDINGS.get(
        modality, _MODALITY_FINDINGS[Modality.OTHER]
    )
    return DetectionResult(
        boxes=boxes,
        classifications=classifications,
        findings_text=findings,
        provider=provider,
        modality=modality,
        model_version=model_version,
        processing_ms=0,
        raw={"mode": "mock"},
    )
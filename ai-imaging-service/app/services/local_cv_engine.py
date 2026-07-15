"""画素ベース局所CVエンジン（オフライン実用デモ用）

外部クラウドなしで、画像内容に応じた病変「候補」枠・分類・所見を生成する。
確定診断用途ではない。OpenCV があれば高精度、なければ NumPy/Pillow にフォールバック。
"""

from __future__ import annotations

import time
from dataclasses import dataclass
from pathlib import Path
from typing import Optional

import numpy as np
from PIL import Image

from app.models.schemas import (
    AiProvider,
    BoundingBox,
    ClassificationResult,
    DetectionResult,
    Modality,
)

try:
    import cv2  # type: ignore

    HAS_CV2 = True
except Exception:
    HAS_CV2 = False


@dataclass
class EngineConfig:
    analysis_size: int = 384
    max_boxes: int = 5
    min_confidence: float = 0.35
    nms_iou: float = 0.35
    model_version: str = "local-cv-1.1"


CONFIG = EngineConfig()


def analyze_image_file(
    image_path: Path,
    modality: Modality,
    preview_path: Optional[Path] = None,
    provider: AiProvider = AiProvider.INHOUSE,
) -> DetectionResult:
    start = time.perf_counter()
    gray, rgb = _load_arrays(image_path, preview_path)
    boxes, classifications, findings = _analyze_arrays(gray, rgb, modality)
    boxes = _nms(boxes, CONFIG.nms_iou)[: CONFIG.max_boxes]
    boxes = [b for b in boxes if b.confidence >= CONFIG.min_confidence]
    if not boxes:
        boxes, classifications, findings = _fallback_low_confidence(modality)

    return DetectionResult(
        boxes=boxes,
        classifications=classifications,
        findings_text=findings,
        provider=provider,
        modality=modality,
        model_version=CONFIG.model_version + ("+cv2" if HAS_CV2 else "+numpy"),
        processing_ms=int((time.perf_counter() - start) * 1000),
        raw={
            "engine": "local_cv",
            "opencv": HAS_CV2,
            "analysis_size": CONFIG.analysis_size,
            "box_count": len(boxes),
            "disclaimer": "assistive_not_diagnostic",
        },
    )


def _load_arrays(
    image_path: Path, preview_path: Optional[Path]
) -> tuple[np.ndarray, Optional[np.ndarray]]:
    path = preview_path if preview_path and preview_path.exists() else image_path
    with Image.open(path) as img:
        img = img.convert("RGB")
        img.thumbnail((CONFIG.analysis_size, CONFIG.analysis_size))
        rgb = np.asarray(img, dtype=np.float32) / 255.0
    gray = (
        0.2989 * rgb[:, :, 0] + 0.5870 * rgb[:, :, 1] + 0.1140 * rgb[:, :, 2]
    ).astype(np.float32)
    return gray, rgb


def _analyze_arrays(
    gray: np.ndarray, rgb: Optional[np.ndarray], modality: Modality
) -> tuple[list[BoundingBox], list[ClassificationResult], str]:
    if modality in (Modality.ENDOSCOPY,) and rgb is not None:
        return _analyze_endoscopy(rgb, gray)
    if modality in (Modality.PATHOLOGY,) and rgb is not None:
        return _analyze_pathology(rgb, gray)
    if modality in (Modality.ULTRASOUND,):
        return _analyze_ultrasound(gray)
    if modality in (Modality.MRI,):
        return _analyze_mri(gray)
    if modality in (Modality.CT,):
        return _analyze_ct(gray)
    # XRAY / DICOM / OTHER
    return _analyze_xray_like(gray, modality)


def _saliency_map(gray: np.ndarray) -> np.ndarray:
    """局所コントラスト + 勾配による注目度マップ"""
    g = _normalize(gray)
    blur = _box_blur(g, k=15)
    local = np.abs(g - blur)
    if HAS_CV2:
        gx = cv2.Sobel(g, cv2.CV_32F, 1, 0, ksize=3)
        gy = cv2.Sobel(g, cv2.CV_32F, 0, 1, ksize=3)
        grad = _normalize(np.abs(gx) + np.abs(gy))
        # 細かいノイズ抑制
        sal = _normalize(0.55 * local + 0.45 * grad)
        sal = cv2.GaussianBlur(sal, (5, 5), 0)
    else:
        gx = np.abs(np.diff(g, axis=1, prepend=g[:, :1]))
        gy = np.abs(np.diff(g, axis=0, prepend=g[:1, :]))
        grad = _normalize(gx + gy)
        sal = _normalize(0.55 * local + 0.45 * grad)
    # 端の縁を抑制
    sal = sal * _edge_mask(sal.shape)
    return sal


def _analyze_xray_like(
    gray: np.ndarray, modality: Modality
) -> tuple[list[BoundingBox], list[ClassificationResult], str]:
    sal = _saliency_map(gray)
    # 肺野寄りの重み（左右）
    h, w = gray.shape
    xx = np.linspace(0, 1, w, dtype=np.float32)
    yy = np.linspace(0, 1, h, dtype=np.float32)[:, None]
    lung_prior = np.exp(-((xx[None, :] - 0.28) ** 2) / 0.08) + np.exp(
        -((xx[None, :] - 0.72) ** 2) / 0.08
    )
    lung_prior = lung_prior * np.exp(-((yy - 0.45) ** 2) / 0.18)
    lung_prior = _normalize(np.broadcast_to(lung_prior, gray.shape).astype(np.float32))
    score = _normalize(0.65 * sal + 0.35 * lung_prior * sal)

    boxes = _peaks_to_boxes(score, labels=("浸潤影候補", "結節影候補", "異常陰影候補"))
    mean_sal = float(score.mean())
    max_sal = float(score.max()) if score.size else 0.0
    abnormal = max_sal > 0.55 and mean_sal > 0.12
    classifications = [
        ClassificationResult(
            label="異常所見候補あり" if abnormal else "明らかな高コントラスト異常は限定的",
            confidence=float(np.clip(0.45 + max_sal * 0.45, 0.4, 0.92)),
            category="abnormality",
        ),
        ClassificationResult(
            label="要精査" if abnormal else "経過観察候補",
            confidence=float(np.clip(0.4 + mean_sal * 0.8, 0.35, 0.85)),
            category="triage",
        ),
    ]
    name = "胸部X線" if modality == Modality.XRAY else modality.value
    findings = (
        f"{name}画像の画素コントラスト解析により、"
        f"{len(boxes)}件の注目領域候補を抽出しました。"
        "肺野相当領域の局所輝度差・勾配に基づく支援情報です。"
        "アーチファクトや正常構造の誤検出があり得ます。"
        "最終判断は医師が原画像を確認のうえ行ってください。"
    )
    return boxes, classifications, findings


def _analyze_ct(gray: np.ndarray):
    sal = _saliency_map(gray)
    # 中心付近の肺/縦隔バランス
    h, w = gray.shape
    cy, cx = h // 2, w // 2
    yy, xx = np.ogrid[:h, :w]
    ring = ((yy - cy) ** 2 + (xx - cx) ** 2).astype(np.float32)
    ring = _normalize(np.exp(-((np.sqrt(ring) / (0.35 * min(h, w))) ** 2)))
    score = _normalize(sal * (0.4 + 0.6 * (1.0 - ring * 0.5)))
    boxes = _peaks_to_boxes(score, labels=("すりガラス影候補", "結節候補", "高吸収域候補"))
    max_sal = float(score.max())
    classifications = [
        ClassificationResult(
            label="肺病変候補" if max_sal > 0.5 else "明らかな局所異常は限定的",
            confidence=float(np.clip(0.5 + max_sal * 0.4, 0.4, 0.9)),
            category="abnormality",
        )
    ]
    findings = (
        "CT断面の局所コントラスト解析により病変候補領域を抽出しました。"
        "単一スライス解析のため、連続切片での確認が必要です。"
        "本結果は診断支援候補であり確定診断ではありません。"
    )
    return boxes, classifications, findings


def _analyze_mri(gray: np.ndarray):
    sal = _saliency_map(gray)
    # 高信号寄り
    bright = _normalize(np.clip(gray - np.percentile(gray, 70), 0, None))
    score = _normalize(0.5 * sal + 0.5 * bright * sal)
    boxes = _peaks_to_boxes(score, labels=("高信号域候補", "異常信号候補", "局所病変候補"))
    classifications = [
        ClassificationResult(
            label="異常信号候補あり",
            confidence=float(np.clip(0.48 + float(score.max()) * 0.4, 0.4, 0.9)),
            category="abnormality",
        )
    ]
    findings = (
        "MRI画像の高信号・局所コントラストに基づき注目領域候補を検出しました。"
        "シーケンス依存性が大きいため、臨床情報と合わせて医師が判断してください。"
    )
    return boxes, classifications, findings


def _analyze_ultrasound(gray: np.ndarray):
    sal = _saliency_map(gray)
    dark = _normalize(np.clip(np.percentile(gray, 40) - gray, 0, None))
    score = _normalize(0.45 * sal + 0.55 * dark)
    boxes = _peaks_to_boxes(score, labels=("低エコー領域候補", "嚢胞様構造候補", "異常領域候補"))
    classifications = [
        ClassificationResult(
            label="低エコー病変候補",
            confidence=float(np.clip(0.45 + float(score.max()) * 0.4, 0.4, 0.88)),
            category="abnormality",
        )
    ]
    findings = (
        "超音波画像の低エコー・局所コントラストから候補領域を抽出しました。"
        "プローブ角度・ゲイン設定の影響を受けやすい点に注意してください。"
    )
    return boxes, classifications, findings


def _analyze_endoscopy(rgb: np.ndarray, gray: np.ndarray):
    r, g, b = rgb[:, :, 0], rgb[:, :, 1], rgb[:, :, 2]
    redness = _normalize(np.clip(r - 0.55 * g - 0.2 * b, 0, None))
    sal = _saliency_map(gray)
    score = _normalize(0.7 * redness + 0.3 * sal)
    boxes = _peaks_to_boxes(score, labels=("発赤・びらん候補", "粘膜異常候補", "出血疑い候補"))
    classifications = [
        ClassificationResult(
            label="粘膜異常候補",
            confidence=float(np.clip(0.5 + float(score.max()) * 0.4, 0.4, 0.9)),
            category="abnormality",
        )
    ]
    findings = (
        "内視鏡画像の赤み成分と局所コントラストから粘膜異常候補を抽出しました。"
        "照明ムラによる誤検出があり得ます。医師による確認が必須です。"
    )
    return boxes, classifications, findings


def _analyze_pathology(rgb: np.ndarray, gray: np.ndarray):
    r, g, b = rgb[:, :, 0], rgb[:, :, 1], rgb[:, :, 2]
    # H&E 系の青紫核寄り
    nuclei = _normalize(np.clip(b * 0.6 + r * 0.1 - g * 0.35, 0, None))
    sal = _saliency_map(gray)
    score = _normalize(0.6 * nuclei + 0.4 * sal)
    boxes = _peaks_to_boxes(score, labels=("異型細胞集簇候補", "高密度核領域", "要確認領域"))
    classifications = [
        ClassificationResult(
            label="要病理医確認",
            confidence=float(np.clip(0.55 + float(score.max()) * 0.35, 0.45, 0.9)),
            category="risk",
        )
    ]
    findings = (
        "病理画像の核密度・色分布に基づく注目領域候補です。"
        "染色条件に強く依存し、確定診断には病理医の評価が必要です。"
    )
    return boxes, classifications, findings


def _peaks_to_boxes(
    score: np.ndarray, labels: tuple[str, ...]
) -> list[BoundingBox]:
    h, w = score.shape
    peaks = _find_peaks(score, max_peaks=len(labels) + 2)
    boxes: list[BoundingBox] = []
    for i, (y, x, conf) in enumerate(peaks):
        # 局所窓サイズを適応
        win = max(h, w) // 8
        y0 = max(0, y - win)
        y1 = min(h, y + win)
        x0 = max(0, x - win)
        x1 = min(w, x + win)
        patch = score[y0:y1, x0:x1]
        if patch.size == 0:
            continue
        # 閾値でタイトな枠に縮める
        thr = float(patch.mean() + 0.35 * patch.std())
        mask = patch >= thr
        if HAS_CV2:
            mask_u8 = (mask.astype(np.uint8) * 255)
            mask_u8 = cv2.morphologyEx(
                mask_u8, cv2.MORPH_CLOSE, np.ones((5, 5), np.uint8)
            )
            mask = mask_u8 > 0
        ys, xs = np.where(mask)
        if len(xs) < 8:
            bw = bh = max(0.08, win * 2 / max(w, h))
            bx = float(np.clip((x / w) - bw / 2, 0, 1 - bw))
            by = float(np.clip((y / h) - bh / 2, 0, 1 - bh))
        else:
            bx = float((xs.min() + x0) / w)
            by = float((ys.min() + y0) / h)
            bw = float(max(0.06, (xs.max() - xs.min() + 1) / w))
            bh = float(max(0.06, (ys.max() - ys.min() + 1) / h))
            if bx + bw > 1:
                bw = 1 - bx
            if by + bh > 1:
                bh = 1 - by
        label = labels[min(i, len(labels) - 1)]
        boxes.append(
            BoundingBox(
                x=round(bx, 4),
                y=round(by, 4),
                width=round(bw, 4),
                height=round(bh, 4),
                label=label,
                confidence=round(float(np.clip(conf, 0.35, 0.95)), 4),
                finding_code=f"LCV-{i+1}",
            )
        )
    return boxes


def _find_peaks(score: np.ndarray, max_peaks: int = 5) -> list[tuple[int, int, float]]:
    s = score.copy()
    h, w = s.shape
    peaks: list[tuple[int, int, float]] = []
    suppress = max(8, min(h, w) // 10)
    for _ in range(max_peaks):
        idx = int(np.argmax(s))
        y, x = divmod(idx, w)
        val = float(s[y, x])
        if val < 0.25:
            break
        peaks.append((y, x, 0.4 + 0.55 * val))
        y0, y1 = max(0, y - suppress), min(h, y + suppress + 1)
        x0, x1 = max(0, x - suppress), min(w, x + suppress + 1)
        s[y0:y1, x0:x1] = 0
    return peaks


def _nms(boxes: list[BoundingBox], iou_thr: float) -> list[BoundingBox]:
    if not boxes:
        return []
    order = sorted(boxes, key=lambda b: b.confidence, reverse=True)
    keep: list[BoundingBox] = []
    while order:
        best = order.pop(0)
        keep.append(best)
        order = [b for b in order if _iou(best, b) < iou_thr]
    return keep


def _iou(a: BoundingBox, b: BoundingBox) -> float:
    ax2, ay2 = a.x + a.width, a.y + a.height
    bx2, by2 = b.x + b.width, b.y + b.height
    ix1, iy1 = max(a.x, b.x), max(a.y, b.y)
    ix2, iy2 = min(ax2, bx2), min(ay2, by2)
    iw, ih = max(0.0, ix2 - ix1), max(0.0, iy2 - iy1)
    inter = iw * ih
    union = a.width * a.height + b.width * b.height - inter
    return inter / union if union > 0 else 0.0


def _fallback_low_confidence(
    modality: Modality,
) -> tuple[list[BoundingBox], list[ClassificationResult], str]:
    box = BoundingBox(
        x=0.35,
        y=0.35,
        width=0.3,
        height=0.3,
        label="低信頼度・要目視確認領域",
        confidence=0.4,
        finding_code="LCV-LOW",
    )
    classifications = [
        ClassificationResult(
            label="明確な異常ピークなし（目視確認推奨）",
            confidence=0.55,
            category="triage",
        )
    ]
    findings = (
        f"{modality.value}画像から強い局所異常ピークは検出されませんでした。"
        "見逃しを否定できないため、全視野の目視確認を推奨します。"
    )
    return [box], classifications, findings


def _normalize(arr: np.ndarray) -> np.ndarray:
    arr = arr.astype(np.float32)
    mn, mx = float(arr.min()), float(arr.max())
    if mx - mn < 1e-8:
        return np.zeros_like(arr, dtype=np.float32)
    return (arr - mn) / (mx - mn)


def _box_blur(arr: np.ndarray, k: int = 15) -> np.ndarray:
    if HAS_CV2:
        k = k if k % 2 == 1 else k + 1
        return cv2.blur(arr, (k, k))
    # ベクトル化積分画像ボックスフィルタ（O(HW)）
    k = max(3, int(k))
    pad = k // 2
    padded = np.pad(arr.astype(np.float64), pad, mode="edge")
    integral = np.pad(padded, ((1, 0), (1, 0)), mode="constant")
    integral = np.cumsum(np.cumsum(integral, axis=0), axis=1)
    h, w = arr.shape
    y0 = np.arange(h)
    x0 = np.arange(w)
    # broadcasting windows
    yy0 = y0[:, None]
    xx0 = x0[None, :]
    s = (
        integral[yy0 + k, xx0 + k]
        - integral[yy0, xx0 + k]
        - integral[yy0 + k, xx0]
        + integral[yy0, xx0]
    )
    return (s / float(k * k)).astype(np.float32)

def _edge_mask(shape: tuple[int, int], margin: float = 0.06) -> np.ndarray:
    h, w = shape
    yy = np.linspace(0, 1, h)[:, None]
    xx = np.linspace(0, 1, w)[None, :]
    mask = (
        (yy > margin)
        & (yy < 1 - margin)
        & (xx > margin)
        & (xx < 1 - margin)
    ).astype(np.float32)
    return mask

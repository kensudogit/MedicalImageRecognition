"""DICOMメタデータ抽出・プレビュー生成"""

from pathlib import Path
from typing import Optional, Tuple

import numpy as np
from PIL import Image

from app.models.schemas import DicomMetadata, Modality


DICOM_EXTENSIONS = {".dcm", ".dicom", ".DCM", ".DICOM"}


def is_dicom_file(path: Path) -> bool:
    if path.suffix in DICOM_EXTENSIONS:
        return True
    try:
        import pydicom
        pydicom.dcmread(str(path), stop_before_pixels=True)
        return True
    except Exception:
        return False


def extract_dicom_metadata(path: Path) -> DicomMetadata:
    import pydicom

    ds = pydicom.dcmread(str(path), stop_before_pixels=False)
    return DicomMetadata(
        patient_id=_tag(ds, "PatientID"),
        patient_name=str(getattr(ds, "PatientName", "") or "") or None,
        study_instance_uid=_tag(ds, "StudyInstanceUID"),
        series_instance_uid=_tag(ds, "SeriesInstanceUID"),
        sop_instance_uid=_tag(ds, "SOPInstanceUID"),
        modality=_tag(ds, "Modality"),
        study_date=_tag(ds, "StudyDate"),
        study_description=_tag(ds, "StudyDescription"),
        series_description=_tag(ds, "SeriesDescription"),
        rows=int(ds.Rows) if hasattr(ds, "Rows") else None,
        columns=int(ds.Columns) if hasattr(ds, "Columns") else None,
        manufacturer=_tag(ds, "Manufacturer"),
        institution_name=_tag(ds, "InstitutionName"),
    )


def _tag(ds, name: str) -> Optional[str]:
    value = getattr(ds, name, None)
    if value is None:
        return None
    return str(value)


def modality_from_dicom(meta: DicomMetadata) -> Modality:
    m = (meta.modality or "").upper()
    mapping = {
        "CR": Modality.XRAY,
        "DX": Modality.XRAY,
        "XA": Modality.XRAY,
        "CT": Modality.CT,
        "MR": Modality.MRI,
        "US": Modality.ULTRASOUND,
        "ES": Modality.ENDOSCOPY,
        "SM": Modality.PATHOLOGY,
        "XC": Modality.PATHOLOGY,
    }
    return mapping.get(m, Modality.DICOM)


def dicom_to_preview_png(path: Path, output_path: Path) -> Path:
    """DICOMピクセルデータをPNGプレビューに変換"""
    import pydicom

    ds = pydicom.dcmread(str(path))
    pixels = ds.pixel_array.astype(np.float64)

    if pixels.ndim == 3:
        # RGB or multi-frame: use first frame / as-is
        if pixels.shape[0] < 5:
            frame = pixels[0]
        else:
            frame = pixels
    else:
        frame = pixels

    if frame.ndim == 2:
        frame = _window_normalize(frame, ds)
        image = Image.fromarray(frame, mode="L")
    else:
        image = Image.fromarray(frame.astype(np.uint8))

    output_path.parent.mkdir(parents=True, exist_ok=True)
    image.save(str(output_path), format="PNG")
    return output_path


def _window_normalize(frame: np.ndarray, ds) -> np.ndarray:
    center = getattr(ds, "WindowCenter", None)
    width = getattr(ds, "WindowWidth", None)
    if center is not None and width is not None:
        try:
            c = float(center[0] if isinstance(center, (list, tuple)) else center)
            w = float(width[0] if isinstance(width, (list, tuple)) else width)
            low = c - w / 2
            high = c + w / 2
            frame = np.clip(frame, low, high)
        except Exception:
            pass
    mn, mx = float(frame.min()), float(frame.max())
    if mx <= mn:
        return np.zeros_like(frame, dtype=np.uint8)
    normalized = ((frame - mn) / (mx - mn) * 255.0).astype(np.uint8)
    return normalized


def image_to_preview(path: Path, output_path: Path, max_size: int = 1024) -> Path:
    """通常画像のプレビュー生成"""
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with Image.open(path) as img:
        img = img.convert("RGB")
        img.thumbnail((max_size, max_size))
        img.save(str(output_path), format="PNG")
    return output_path


def detect_modality_from_filename(filename: str) -> Modality:
    lower = filename.lower()
    if any(x in lower for x in (".dcm", "dicom")):
        return Modality.DICOM
    if "xray" in lower or "xp" in lower or "chest" in lower:
        return Modality.XRAY
    if "ct" in lower:
        return Modality.CT
    if "mri" in lower or "mr_" in lower:
        return Modality.MRI
    if "us" in lower or "ultrasound" in lower or "echo" in lower:
        return Modality.ULTRASOUND
    if "endo" in lower or "gastro" in lower:
        return Modality.ENDOSCOPY
    if "path" in lower or "histo" in lower:
        return Modality.PATHOLOGY
    return Modality.OTHER

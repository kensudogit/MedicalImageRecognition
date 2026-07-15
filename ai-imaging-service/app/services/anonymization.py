"""DICOM PHI 匿名化（Basic Application Level Confidentiality Profile 準拠の簡易実装）"""

from pathlib import Path
from typing import Optional

# DICOMタグ（キーワード）で除去・置換する項目
PHI_TAGS_TO_REMOVE = {
    "PatientName",
    "PatientID",
    "PatientBirthDate",
    "PatientSex",
    "PatientAddress",
    "PatientTelephoneNumbers",
    "OtherPatientIDs",
    "OtherPatientNames",
    "EthnicGroup",
    "Occupation",
    "AdditionalPatientHistory",
    "PatientComments",
    "InstitutionAddress",
    "ReferringPhysicianName",
    "PerformingPhysicianName",
    "OperatorsName",
    "RequestingPhysician",
}


def anonymize_dicom_file(source: Path, destination: Path, replacement_id: str = "ANONYMIZED") -> Path:
    import pydicom
    from pydicom.uid import generate_uid

    ds = pydicom.dcmread(str(source))
    for tag in PHI_TAGS_TO_REMOVE:
        if hasattr(ds, tag):
            try:
                delattr(ds, tag)
            except Exception:
                pass

    ds.PatientName = "ANONYMIZED"
    ds.PatientID = replacement_id
    if hasattr(ds, "PatientBirthDate"):
        ds.PatientBirthDate = ""

    # Study/Series UID は追跡性のため維持（運用方針で再採番も可）
    if not getattr(ds, "StudyInstanceUID", None):
        ds.StudyInstanceUID = generate_uid()
    if not getattr(ds, "SeriesInstanceUID", None):
        ds.SeriesInstanceUID = generate_uid()
    if not getattr(ds, "SOPInstanceUID", None):
        ds.SOPInstanceUID = generate_uid()

    destination.parent.mkdir(parents=True, exist_ok=True)
    ds.save_as(str(destination))
    return destination


def redact_metadata_dict(meta: dict, alias: Optional[str] = None) -> dict:
    redacted = dict(meta)
    redacted["patient_name"] = "ANONYMIZED"
    redacted["patient_id"] = alias or "ANONYMIZED"
    return redacted

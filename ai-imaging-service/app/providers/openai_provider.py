"""OpenAI Vision プロバイダー（GPT-4o 等）"""

from __future__ import annotations

import base64
import json
import re
import time
from pathlib import Path
from typing import Any, Optional

import httpx
from PIL import Image

from app.config import settings
from app.models.schemas import (
    AiProvider,
    AnalyzeRequest,
    BoundingBox,
    ClassificationResult,
    DetectionResult,
    Modality,
)
from app.providers.base import BaseImagingProvider
from app.providers.fallback import practical_fallback


class OpenAiProvider(BaseImagingProvider):
    provider = AiProvider.OPENAI

    async def is_available(self) -> bool:
        if settings.openai_api_key:
            return True
        return settings.use_local_cv or settings.enable_mock_inference

    async def analyze(
        self,
        image_path: Path,
        modality: Modality,
        request: AnalyzeRequest,
        preview_path: Optional[Path] = None,
    ) -> DetectionResult:
        if not settings.openai_api_key or settings.force_local_cv:
            return await practical_fallback(
                image_path,
                modality,
                AiProvider.OPENAI,
                preview_path,
                "openai-mock",
            )

        start = time.perf_counter()
        data_url = _image_to_data_url(preview_path or image_path, image_path)
        payload = _build_chat_payload(data_url, modality, request)

        headers = {
            "Authorization": f"Bearer {settings.openai_api_key}",
            "Content-Type": "application/json",
        }
        if settings.openai_organization:
            headers["OpenAI-Organization"] = settings.openai_organization

        base = settings.openai_base_url.rstrip("/")
        async with httpx.AsyncClient(timeout=settings.openai_timeout_seconds) as client:
            response = await client.post(
                f"{base}/chat/completions",
                headers=headers,
                json=payload,
            )
            if response.status_code >= 400:
                detail = response.text[:500]
                raise RuntimeError(f"OpenAI API error {response.status_code}: {detail}")
            data = response.json()

        content = _extract_message_content(data)
        parsed = _parse_structured_result(content)
        boxes = [_to_box(b, i) for i, b in enumerate(parsed.get("boxes") or [])]
        boxes = [b for b in boxes if b is not None][:8]
        classifications = [
            _to_classification(c) for c in (parsed.get("classifications") or [])
        ]
        classifications = [c for c in classifications if c is not None][:6]

        findings = str(parsed.get("findings_text") or "").strip()
        if not findings and request.generate_findings:
            findings = content.strip()[:2000] or (
                "OpenAI Vision の解析結果を取得しました。"
                "本結果は診断支援候補であり確定診断ではありません。"
            )
        if "確定診断" not in findings and "診断支援" not in findings:
            findings += (
                "\n\n本結果は OpenAI Vision による診断支援候補です。"
                "最終判断は医師が原画像を確認のうえ行ってください。"
            )

        usage = data.get("usage") or {}
        return DetectionResult(
            boxes=boxes,
            classifications=classifications,
            findings_text=findings,
            provider=AiProvider.OPENAI,
            modality=modality,
            model_version=settings.openai_model,
            processing_ms=int((time.perf_counter() - start) * 1000),
            raw={
                "engine": "openai_vision",
                "model": settings.openai_model,
                "usage": usage,
                "id": data.get("id"),
                "parsed": parsed,
                "disclaimer": "assistive_not_diagnostic",
            },
        )


def _image_to_data_url(preferred: Path, fallback: Path) -> str:
    path = preferred if preferred and preferred.exists() else fallback
    # DICOM 等はプレビュー必須。未生成なら Pillow で読めない場合がある
    try:
        with Image.open(path) as img:
            img = img.convert("RGB")
            img.thumbnail((settings.preview_max_size, settings.preview_max_size))
            import io

            buf = io.BytesIO()
            img.save(buf, format="JPEG", quality=85, optimize=True)
            encoded = base64.b64encode(buf.getvalue()).decode("ascii")
            return f"data:image/jpeg;base64,{encoded}"
    except Exception:
        raw = path.read_bytes()
        encoded = base64.b64encode(raw).decode("ascii")
        suffix = path.suffix.lower()
        mime = {
            ".png": "image/png",
            ".jpg": "image/jpeg",
            ".jpeg": "image/jpeg",
            ".webp": "image/webp",
            ".gif": "image/gif",
        }.get(suffix, "application/octet-stream")
        return f"data:{mime};base64,{encoded}"


def _build_chat_payload(
    data_url: str, modality: Modality, request: AnalyzeRequest
) -> dict[str, Any]:
    context = request.patient_context or "（なし）"
    system = (
        "あなたは医療画像の診断支援アシスタントです。"
        "確定診断は行わず、医師が確認すべき候補所見のみを提示します。"
        "必ず指定の JSON だけを返してください。説明文や Markdown は禁止です。"
    )
    user_text = (
        f"モダリティ: {modality.value}\n"
        f"臨床情報: {context}\n"
        "画像を解析し、次の JSON スキーマで返してください。\n"
        "{\n"
        '  "boxes": [\n'
        '    {"x":0.0,"y":0.0,"width":0.1,"height":0.1,'
        '"label":"所見ラベル","confidence":0.0,"finding_code":"CODE"}\n'
        "  ],\n"
        '  "classifications": [\n'
        '    {"label":"分類ラベル","confidence":0.0,"category":"abnormality"}\n'
        "  ],\n"
        '  "findings_text": "日本語の所見文（支援情報である旨を含む）"\n'
        "}\n"
        "制約:\n"
        "- boxes の座標は画像全体に対する正規化値 0.0–1.0（左上が原点）\n"
        "- 明確な候補がなければ boxes は空配列でもよい\n"
        "- confidence は 0.0–1.0\n"
        "- 過度に断定的な診断名は避け、「候補」「疑い」表現を使う\n"
    )
    return {
        "model": settings.openai_model,
        "temperature": 0.2,
        "max_tokens": settings.openai_max_tokens,
        "response_format": {"type": "json_object"},
        "messages": [
            {"role": "system", "content": system},
            {
                "role": "user",
                "content": [
                    {"type": "text", "text": user_text},
                    {
                        "type": "image_url",
                        "image_url": {"url": data_url, "detail": "high"},
                    },
                ],
            },
        ],
    }


def _extract_message_content(data: dict[str, Any]) -> str:
    try:
        return data["choices"][0]["message"]["content"] or ""
    except (KeyError, IndexError, TypeError):
        return ""


def _parse_structured_result(content: str) -> dict[str, Any]:
    text = (content or "").strip()
    if not text:
        return {}
    try:
        data = json.loads(text)
        return data if isinstance(data, dict) else {}
    except json.JSONDecodeError:
        match = re.search(r"\{[\s\S]*\}", text)
        if not match:
            return {"findings_text": text}
        try:
            data = json.loads(match.group(0))
            return data if isinstance(data, dict) else {"findings_text": text}
        except json.JSONDecodeError:
            return {"findings_text": text}


def _clip01(v: Any, default: float = 0.0) -> float:
    try:
        x = float(v)
    except (TypeError, ValueError):
        return default
    return max(0.0, min(1.0, x))


def _to_box(item: Any, index: int) -> Optional[BoundingBox]:
    if not isinstance(item, dict):
        return None
    label = str(item.get("label") or f"候補領域{index + 1}").strip()
    width = _clip01(item.get("width"), 0.1)
    height = _clip01(item.get("height"), 0.1)
    x = _clip01(item.get("x"), 0.0)
    y = _clip01(item.get("y"), 0.0)
    if x + width > 1.0:
        width = max(0.02, 1.0 - x)
    if y + height > 1.0:
        height = max(0.02, 1.0 - y)
    return BoundingBox(
        x=round(x, 4),
        y=round(y, 4),
        width=round(width, 4),
        height=round(height, 4),
        label=label,
        confidence=round(_clip01(item.get("confidence"), 0.5), 4),
        finding_code=str(item.get("finding_code") or f"OAI-{index + 1}"),
    )


def _to_classification(item: Any) -> Optional[ClassificationResult]:
    if not isinstance(item, dict):
        return None
    label = str(item.get("label") or "").strip()
    if not label:
        return None
    return ClassificationResult(
        label=label,
        confidence=round(_clip01(item.get("confidence"), 0.5), 4),
        category=str(item.get("category") or "") or None,
    )

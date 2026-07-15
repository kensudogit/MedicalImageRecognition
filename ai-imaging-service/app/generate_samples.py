"""デモ用サンプル医療画像を生成するスクリプト"""

from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageFilter


OUT_DIR = Path(__file__).resolve().parent / "static" / "samples"


def _font(size: int = 18):
    for name in (
        "C:/Windows/Fonts/meiryo.ttc",
        "C:/Windows/Fonts/msgothic.ttc",
        "C:/Windows/Fonts/arial.ttf",
    ):
        try:
            return ImageFont.truetype(name, size)
        except Exception:
            continue
    return ImageFont.load_default()


def _label(draw: ImageDraw.ImageDraw, text: str, xy=(12, 12)):
    font = _font(16)
    x, y = xy
    draw.rectangle([x - 4, y - 2, x + 210, y + 22], fill=(0, 0, 0, 160))
    draw.text((x, y), text, fill=(230, 240, 255), font=font)


def make_xray(path: Path):
    w, h = 512, 640
    base = np.zeros((h, w), dtype=np.float32)
    yy, xx = np.mgrid[0:h, 0:w]
    # lung fields
    left = np.exp(-(((xx - 170) / 95) ** 2 + ((yy - 300) / 180) ** 2))
    right = np.exp(-(((xx - 340) / 95) ** 2 + ((yy - 300) / 180) ** 2))
    heart = np.exp(-(((xx - 270) / 70) ** 2 + ((yy - 360) / 110) ** 2)) * 0.55
    ribs = 0.08 * np.sin(yy / 18) * np.exp(-((xx - 255) / 180) ** 2)
    base = 0.15 + 0.55 * (left + right) + heart + ribs
    # synthetic infiltrate candidate (upper right)
    lesion = np.exp(-(((xx - 360) / 35) ** 2 + ((yy - 180) / 28) ** 2)) * 0.35
    base = np.clip(base + lesion, 0, 1)
    img = Image.fromarray((base * 255).astype(np.uint8), mode="L").convert("RGBA")
    draw = ImageDraw.Draw(img, "RGBA")
    _label(draw, "SAMPLE X-RAY (demo)")
    img.convert("RGB").save(path, quality=92)


def make_ct(path: Path):
    w, h = 512, 512
    yy, xx = np.mgrid[0:h, 0:w]
    cx, cy = 256, 256
    r = np.sqrt((xx - cx) ** 2 + (yy - cy) ** 2)
    body = (r < 220).astype(np.float32)
    lung = ((r > 70) & (r < 200)).astype(np.float32) * 0.25
    mediastinum = (r < 70).astype(np.float32) * 0.55
    # GGO-like patch
    ggo = np.exp(-(((xx - 330) / 40) ** 2 + ((yy - 200) / 35) ** 2)) * 0.45
    noise = np.random.default_rng(42).normal(0, 0.02, (h, w))
    base = np.clip(0.08 * body + lung + mediastinum + ggo + noise, 0, 1)
    img = Image.fromarray((base * 255).astype(np.uint8), mode="L").convert("RGBA")
    draw = ImageDraw.Draw(img, "RGBA")
    _label(draw, "SAMPLE CT (demo)")
    # soft circle outline
    draw.ellipse([36, 36, 476, 476], outline=(180, 180, 180, 80), width=2)
    img.convert("RGB").save(path, quality=92)


def make_mri(path: Path):
    w, h = 512, 512
    yy, xx = np.mgrid[0:h, 0:w]
    brain = np.exp(-(((xx - 256) / 150) ** 2 + ((yy - 260) / 170) ** 2))
    ventricle = np.exp(-(((xx - 256) / 35) ** 2 + ((yy - 250) / 50) ** 2)) * 0.6
    lesion = np.exp(-(((xx - 190) / 22) ** 2 + ((yy - 220) / 18) ** 2)) * 0.9
    base = np.clip(0.2 + 0.55 * brain - ventricle + lesion, 0, 1)
    # T2-like teal tint
    rgb = np.zeros((h, w, 3), dtype=np.uint8)
    g = (base * 220).astype(np.uint8)
    rgb[:, :, 0] = (g * 0.55).astype(np.uint8)
    rgb[:, :, 1] = (g * 0.85).astype(np.uint8)
    rgb[:, :, 2] = g
    img = Image.fromarray(rgb, mode="RGB").convert("RGBA")
    draw = ImageDraw.Draw(img, "RGBA")
    _label(draw, "SAMPLE MRI (demo)")
    img.convert("RGB").save(path, quality=92)


def make_ultrasound(path: Path):
    w, h = 512, 480
    rng = np.random.default_rng(7)
    base = rng.normal(0.35, 0.08, (h, w))
    yy, xx = np.mgrid[0:h, 0:w]
    # sector-ish dark edges
    mask = np.exp(-((xx - 256) / 220) ** 2) * (yy / h)
    cyst = np.exp(-(((xx - 280) / 30) ** 2 + ((yy - 260) / 30) ** 2))
    base = np.clip(base * mask - cyst * 0.35 + 0.15, 0, 1)
    img = Image.fromarray((base * 255).astype(np.uint8), mode="L").convert("RGBA")
    img = img.filter(ImageFilter.GaussianBlur(radius=0.8))
    draw = ImageDraw.Draw(img, "RGBA")
    _label(draw, "SAMPLE US (demo)")
    img.convert("RGB").save(path, quality=92)


def make_endoscopy(path: Path):
    w, h = 512, 384
    yy, xx = np.mgrid[0:h, 0:w]
    mucosa = 0.55 + 0.15 * np.sin(xx / 25) + 0.1 * np.sin(yy / 30)
    vessel = 0.12 * np.sin((xx + yy) / 12) * np.exp(-((yy - 200) / 120) ** 2)
    erosion = np.exp(-(((xx - 250) / 55) ** 2 + ((yy - 200) / 40) ** 2)) * 0.35
    r = np.clip(mucosa + erosion, 0, 1)
    g = np.clip(mucosa * 0.45 - vessel, 0, 1)
    b = np.clip(mucosa * 0.35 - vessel * 0.5, 0, 1)
    rgb = np.stack([(r * 220).astype(np.uint8), (g * 140).astype(np.uint8), (b * 120).astype(np.uint8)], axis=-1)
    img = Image.fromarray(rgb, mode="RGB").convert("RGBA")
    draw = ImageDraw.Draw(img, "RGBA")
    # circular FOV
    overlay = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    od = ImageDraw.Draw(overlay)
    od.ellipse([20, 10, w - 20, h - 10], outline=(0, 0, 0, 0))
    mask = Image.new("L", (w, h), 0)
    ImageDraw.Draw(mask).ellipse([20, 10, w - 20, h - 10], fill=255)
    bg = Image.new("RGB", (w, h), (10, 10, 10))
    composed = Image.composite(img.convert("RGB"), bg, mask).convert("RGBA")
    draw = ImageDraw.Draw(composed, "RGBA")
    _label(draw, "SAMPLE ENDOSCOPY (demo)")
    composed.convert("RGB").save(path, quality=92)


def make_pathology(path: Path):
    w, h = 512, 512
    rng = np.random.default_rng(21)
    # H&E-like pink/purple
    cells = rng.random((h, w))
    nuclei = (rng.random((h // 4, w // 4)) > 0.82).astype(np.float32)
    nuclei = np.array(Image.fromarray((nuclei * 255).astype(np.uint8)).resize((w, h), Image.NEAREST)) / 255.0
    r = np.clip(0.85 - nuclei * 0.35 + cells * 0.05, 0, 1)
    g = np.clip(0.55 - nuclei * 0.25 + cells * 0.08, 0, 1)
    b = np.clip(0.70 + nuclei * 0.2 - cells * 0.05, 0, 1)
    # atypical cluster region
    yy, xx = np.mgrid[0:h, 0:w]
    cluster = np.exp(-(((xx - 280) / 70) ** 2 + ((yy - 250) / 60) ** 2))
    b = np.clip(b + cluster * 0.25, 0, 1)
    r = np.clip(r - cluster * 0.1, 0, 1)
    rgb = np.stack([(r * 255).astype(np.uint8), (g * 255).astype(np.uint8), (b * 255).astype(np.uint8)], axis=-1)
    img = Image.fromarray(rgb, mode="RGB").convert("RGBA")
    draw = ImageDraw.Draw(img, "RGBA")
    _label(draw, "SAMPLE PATHOLOGY (demo)")
    img.convert("RGB").save(path, quality=92)


SAMPLES = [
    ("sample_xray.png", "XRAY", "胸部X線（デモ）", make_xray),
    ("sample_ct.png", "CT", "胸部CT（デモ）", make_ct),
    ("sample_mri.png", "MRI", "頭部MRI（デモ）", make_mri),
    ("sample_ultrasound.png", "ULTRASOUND", "腹部超音波（デモ）", make_ultrasound),
    ("sample_endoscopy.png", "ENDOSCOPY", "内視鏡（デモ）", make_endoscopy),
    ("sample_pathology.png", "PATHOLOGY", "病理画像（デモ）", make_pathology),
]


def generate_all() -> list[dict]:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    meta = []
    for filename, modality, title, fn in SAMPLES:
        path = OUT_DIR / filename
        fn(path)
        meta.append(
            {
                "id": path.stem,
                "filename": filename,
                "modality": modality,
                "title": title,
                "url": f"/samples/{filename}",
            }
        )
    return meta


if __name__ == "__main__":
    items = generate_all()
    print(f"Generated {len(items)} samples in {OUT_DIR}")
    for item in items:
        print(" -", item["filename"], item["modality"])

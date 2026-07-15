"""実用性能ベンチマーク（ローカルCV）"""

from __future__ import annotations

import statistics
import time
from pathlib import Path

from app.generate_samples import OUT_DIR, generate_all
from app.models.schemas import Modality
from app.services.local_cv_engine import analyze_image_file


SAMPLES = [
    ("sample_xray.png", Modality.XRAY),
    ("sample_ct.png", Modality.CT),
    ("sample_mri.png", Modality.MRI),
    ("sample_ultrasound.png", Modality.ULTRASOUND),
    ("sample_endoscopy.png", Modality.ENDOSCOPY),
    ("sample_pathology.png", Modality.PATHOLOGY),
]


def main() -> None:
    if not any(OUT_DIR.glob("*.png")):
        generate_all()

    print("=== Local CV Practical Performance Benchmark ===")
    all_ms: list[float] = []
    for name, modality in SAMPLES:
        path = OUT_DIR / name
        times = []
        boxes_n = 0
        for i in range(5):
            t0 = time.perf_counter()
            result = analyze_image_file(path, modality)
            dt = (time.perf_counter() - t0) * 1000
            times.append(dt)
            boxes_n = len(result.boxes)
        all_ms.extend(times)
        print(
            f"{name:24s} {modality.value:12s} "
            f"avg={statistics.mean(times):6.1f}ms "
            f"p50={statistics.median(times):6.1f}ms "
            f"min={min(times):6.1f}ms "
            f"boxes={boxes_n} model={result.model_version}"
        )

    print("---")
    print(
        f"OVERALL avg={statistics.mean(all_ms):.1f}ms "
        f"p50={statistics.median(all_ms):.1f}ms "
        f"max={max(all_ms):.1f}ms n={len(all_ms)}"
    )
    ok = statistics.mean(all_ms) < 500
    print("PASS" if ok else "WARN: avg latency >= 500ms")


if __name__ == "__main__":
    main()

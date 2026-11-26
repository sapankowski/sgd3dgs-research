"""Export native Gaussian Grouping labels from a trained PLY and classifier."""

from __future__ import annotations

import argparse
import json
import platform
import time
from pathlib import Path

import numpy as np
import torch
from plyfile import PlyData


def export_labels(
    source: Path,
    classifier_path: Path,
    output: Path,
    *,
    selected_ids: tuple[int, ...] = (),
    threshold: float = 0.3,
    chunk_size: int = 65536,
) -> dict:
    """Classify PLY vertices in their original order using the matching checkpoint."""
    started = time.perf_counter()
    vertices = PlyData.read(source)["vertex"].data
    state = torch.load(classifier_path, map_location="cpu", weights_only=True)
    weight = state["weight"][:, :, 0, 0].float()
    bias = state["bias"].float()
    count = len(vertices)
    labels = np.empty(count, dtype=np.int64)
    confidence = np.empty(count, dtype=np.float32)
    mask = np.zeros(count, dtype=np.bool_) if selected_ids else None
    selected_ids = tuple(sorted(set(selected_ids)))

    with torch.inference_mode():
        for start in range(0, count, chunk_size):
            end = min(start + chunk_size, count)
            features = np.column_stack(
                [vertices[f"obj_dc_{i}"][start:end] for i in range(16)]
            ).astype(np.float32)
            logits = torch.nn.functional.linear(torch.from_numpy(features), weight, bias)
            probabilities = torch.softmax(logits, dim=1)
            values, indices = probabilities.max(dim=1)
            labels[start:end] = indices.numpy()
            confidence[start:end] = values.numpy()
            if mask is not None:
                # Match upstream raw selection, before its convex-hull expansion.
                selected = (probabilities[:, list(selected_ids)] > threshold).any(dim=1)
                mask[start:end] = selected.numpy()

    selected_count = int(mask.sum()) if mask is not None else None
    bounding_box = None
    if selected_count:
        xyz = np.column_stack([vertices[name][mask] for name in ("x", "y", "z")])
        bounding_box = {"min": xyz.min(axis=0).tolist(), "max": xyz.max(axis=0).tolist()}
    report = {
        "status": "complete",
        "method": "Gaussian Grouping",
        "reference_upstream_commit": "0ab60afed3385b717c985af1d30a20f7b0884c89",
        "checkpoint_training_commit": None,
        "source": {"name": source.name, "gaussian_count": count},
        "classifier": classifier_path.name,
        "ordering": "source PLY vertex order",
        "native_id": {"dtype": "int64", "shape": [count], "rule": "argmax class"},
        "confidence": {"dtype": "float32", "rule": "maximum softmax probability"},
        "class_count": len(bias),
        "class_histogram": np.bincount(labels, minlength=len(bias)).tolist(),
        "selection": {
            "ids": list(selected_ids),
            "threshold": threshold,
            "rule": "any selected class probability strictly greater than threshold",
            "convex_hull_expansion": False,
            "selected_count": selected_count,
            "selected_fraction": selected_count / count if selected_count is not None else None,
            "bounding_box": bounding_box,
        },
        "device": "cpu",
        "peak_vram_bytes": None,
        "environment": {
            "python": platform.python_version(),
            "torch": torch.__version__,
            "numpy": np.__version__,
            "platform": platform.platform(),
        },
    }

    # Each run owns a new directory. Write the completion report last.
    output.mkdir(parents=True)
    np.save(output / "native_id.npy", labels)
    np.save(output / "confidence.npy", confidence)
    if mask is not None:
        np.save(output / "mask.npy", mask)
    report["runtime_seconds"] = time.perf_counter() - started
    (output / "report.json").write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    return report


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--ply", type=Path, required=True)
    parser.add_argument("--classifier", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--select-id", type=int, action="append", default=[])
    parser.add_argument("--threshold", type=float, default=0.3)
    parser.add_argument("--chunk-size", type=int, default=65536)
    args = parser.parse_args()
    report = export_labels(
        args.ply,
        args.classifier,
        args.output,
        selected_ids=tuple(args.select_id),
        threshold=args.threshold,
        chunk_size=args.chunk_size,
    )
    print(json.dumps(report, indent=2))


if __name__ == "__main__":
    main()

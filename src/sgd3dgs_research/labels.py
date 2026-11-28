"""Convert a per-Gaussian Boolean mask into a canonical schema 0.1 label package."""

from __future__ import annotations

import hashlib
import json
import os
import platform
import shutil
from pathlib import Path
from typing import Any

import numpy as np

UINT16_OBJECT_ID_MIN = 1
UINT16_OBJECT_ID_MAX = 65533


class LabelConversionError(ValueError):
    """Raised when inputs do not match the source scene; nothing is written."""


def sha256_file(path: Path, chunk_size: int = 1024 * 1024) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        while chunk := stream.read(chunk_size):
            digest.update(chunk)
    return digest.hexdigest()


def read_ply_vertex_count(path: Path) -> int:
    """Read `element vertex N` from a PLY header without loading the payload."""
    with path.open("rb") as stream:
        if stream.readline().strip() != b"ply":
            raise LabelConversionError(f"{path.name} is not a PLY file")
        for raw in stream:
            line = raw.decode("ascii", errors="replace").strip()
            if line == "end_header":
                break
            parts = line.split()
            if len(parts) == 3 and parts[0] == "element" and parts[1] == "vertex":
                return int(parts[2])
    raise LabelConversionError(f"{path.name} has no vertex element in its header")


def convert_mask(
    *,
    mask_path: Path,
    source_path: Path,
    manifest_path: Path,
    output_dir: Path,
    object_id: int,
    object_name: str,
    method: str,
    method_version: str,
    run_report_path: Path | None = None,
) -> dict[str, Any]:
    """Write `object_id.npy`, an updated `scene.json`, provenance and checksums.

    Every input is checked before the output directory is created, so a failed
    conversion leaves nothing behind. An existing output directory is never
    reused.
    """
    if output_dir.exists():
        raise LabelConversionError(f"output directory already exists: {output_dir}")
    if not UINT16_OBJECT_ID_MIN <= object_id <= UINT16_OBJECT_ID_MAX:
        raise LabelConversionError(
            f"object_id must be in {UINT16_OBJECT_ID_MIN}..{UINT16_OBJECT_ID_MAX}, got {object_id}"
        )

    manifest: dict[str, Any] = json.loads(manifest_path.read_text(encoding="utf-8"))
    try:
        source = manifest["source"]
        source_relative = str(source["path"])
        expected_sha256 = source["sha256"]
        expected_count = int(source["gaussian_count"])
    except (KeyError, TypeError, ValueError) as missing:
        raise LabelConversionError(
            f"{manifest_path.name} lacks source.path/sha256/gaussian_count"
        ) from missing

    source_sha256 = sha256_file(source_path)
    if source_sha256 != expected_sha256:
        raise LabelConversionError(
            f"source checksum mismatch: manifest expects {expected_sha256}, "
            f"{source_path.name} is {source_sha256}"
        )
    header_count = read_ply_vertex_count(source_path)
    if header_count != expected_count:
        raise LabelConversionError(
            f"Gaussian count mismatch: manifest declares {expected_count}, "
            f"PLY header has {header_count}"
        )

    mask = np.load(mask_path, allow_pickle=False)
    if mask.dtype != np.bool_ or mask.ndim != 1:
        raise LabelConversionError(
            f"mask must be a 1-D Boolean array, got dtype {mask.dtype} with shape {mask.shape}"
        )
    if mask.shape[0] != header_count:
        raise LabelConversionError(
            f"mask length {mask.shape[0]} does not match Gaussian count {header_count}"
        )

    run_report_sha256 = None
    if run_report_path is not None:
        report = json.loads(run_report_path.read_text(encoding="utf-8"))
        report_count = report.get("source", {}).get("gaussian_count")
        if report_count is not None and int(report_count) != header_count:
            raise LabelConversionError(
                f"run report Gaussian count {report_count} does not match {header_count}"
            )
        run_report_sha256 = sha256_file(run_report_path)

    # Order is preserved: index i of the output describes PLY vertex i.
    labels = np.zeros(header_count, dtype=np.uint16)
    labels[mask] = object_id
    selected_count = int(mask.sum())

    output_dir.mkdir(parents=True)
    _link_or_copy(source_path, output_dir / source_relative)
    labels_path = output_dir / "object_id.npy"
    np.save(labels_path, labels)
    labels_sha256 = sha256_file(labels_path)

    manifest["labels"] = {
        "path": "object_id.npy",
        "sha256": labels_sha256,
        "format": "npy-uint16",
        "gaussian_count": header_count,
        "method": method,
        "method_version": method_version,
        "confidence_path": None,
    }
    manifest["objects"] = [
        {
            "object_id": object_id,
            "name": object_name,
            "movable": True,
            "initial_transform": {
                "translation": [0.0, 0.0, 0.0],
                "rotation_xyzw": [0.0, 0.0, 0.0, 1.0],
                "uniform_scale": 1.0,
            },
            "notes": f"{selected_count} Gaussians from {mask_path.name}",
        }
    ]
    (output_dir / "scene.json").write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")

    provenance: dict[str, Any] = {
        "tool": "sgd3dgs-research convert-mask",
        "ordering": "source PLY vertex order",
        "inputs": {
            "mask": {"name": mask_path.name, "sha256": sha256_file(mask_path)},
            "source": {"path": source_relative, "sha256": source_sha256, "count": header_count},
            "manifest_template": {
                "name": manifest_path.name,
                "sha256": sha256_file(manifest_path),
            },
            "run_report": (
                {"name": run_report_path.name, "sha256": run_report_sha256}
                if run_report_path is not None
                else None
            ),
        },
        "output": {
            "object_id": object_id,
            "object_name": object_name,
            "selected_count": selected_count,
            "background_value": 0,
            "labels_sha256": labels_sha256,
        },
        "method": {"name": method, "version": method_version},
        "environment": {
            "python": platform.python_version(),
            "numpy": np.__version__,
        },
    }
    (output_dir / "provenance.json").write_text(
        json.dumps(provenance, indent=2) + "\n", encoding="utf-8"
    )
    _write_checksums(
        output_dir, [source_relative, "object_id.npy", "scene.json", "provenance.json"]
    )
    return provenance


def _link_or_copy(source: Path, destination: Path) -> None:
    """Place the source PLY in the package as a hard link, or a copy if linking fails."""
    destination.parent.mkdir(parents=True, exist_ok=True)
    try:
        os.link(source, destination)
    except OSError:
        shutil.copy2(source, destination)


def _write_checksums(output_dir: Path, relative_paths: list[str]) -> None:
    lines = [f"{sha256_file(output_dir / path)}  {path}" for path in relative_paths]
    (output_dir / "SHA256SUMS").write_text("\n".join(lines) + "\n", encoding="utf-8")

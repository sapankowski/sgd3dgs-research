import json
from pathlib import Path

import numpy as np
import pytest
from typer.testing import CliRunner

from sgd3dgs_research.cli import app
from sgd3dgs_research.labels import (
    LabelConversionError,
    convert_mask,
    read_ply_vertex_count,
    sha256_file,
)

RUNNER = CliRunner()
COUNT = 5


def write_ply(path: Path, count: int = COUNT, marker: str = "a") -> Path:
    rows = "".join(f"{i} 0 0\n" for i in range(count))
    path.write_text(
        "ply\nformat ascii 1.0\n"
        f"comment {marker}\n"
        f"element vertex {count}\n"
        "property float x\nproperty float y\nproperty float z\n"
        f"end_header\n{rows}",
        encoding="ascii",
    )
    return path


def write_manifest(path: Path, source: Path, count: int = COUNT) -> Path:
    manifest = {
        "schema_version": "0.1",
        "scene_id": "fixture",
        "display_name": "Fixture",
        "coordinate_system": {"up_axis": "+Y"},
        "source": {
            "path": "reconstruction/point_cloud.ply",
            "sha256": sha256_file(source),
            "format": "3dgs-ply",
            "gaussian_count": count,
        },
        "cameras": None,
        "labels": None,
        "objects": [],
    }
    path.write_text(json.dumps(manifest), encoding="utf-8")
    return path


@pytest.fixture
def inputs(tmp_path: Path) -> dict[str, Path]:
    source = write_ply(tmp_path / "point_cloud.ply")
    mask = tmp_path / "mask.npy"
    np.save(mask, np.array([True, False, True, False, False]))
    return {
        "source": source,
        "mask": mask,
        "manifest": write_manifest(tmp_path / "scene.json", source),
        "output": tmp_path / "package",
    }


def run(inputs: dict[str, Path], **overrides: object) -> dict[str, object]:
    arguments: dict[str, object] = {
        "mask_path": inputs["mask"],
        "source_path": inputs["source"],
        "manifest_path": inputs["manifest"],
        "output_dir": inputs["output"],
        "object_id": 1,
        "object_name": "yellow bowl",
        "method": "gaussian-grouping",
        "method_version": "class-108-threshold-0.3",
    }
    arguments.update(overrides)
    return convert_mask(**arguments)  # type: ignore[arg-type]


def test_converts_mask_in_source_order(inputs: dict[str, Path]) -> None:
    provenance = run(inputs)

    package = inputs["output"]
    labels = np.load(package / "object_id.npy")
    assert labels.dtype == np.uint16
    assert labels.tolist() == [1, 0, 1, 0, 0]
    assert provenance["output"]["selected_count"] == 2  # type: ignore[index]

    manifest = json.loads((package / "scene.json").read_text(encoding="utf-8"))
    assert manifest["labels"]["sha256"] == sha256_file(package / "object_id.npy")
    assert manifest["labels"]["gaussian_count"] == COUNT
    assert manifest["objects"][0]["object_id"] == 1
    assert sha256_file(package / manifest["source"]["path"]) == manifest["source"]["sha256"]

    for line in (package / "SHA256SUMS").read_text(encoding="utf-8").splitlines():
        digest, relative = line.split("  ")
        assert sha256_file(package / relative) == digest


def test_rejects_wrong_mask_length(inputs: dict[str, Path]) -> None:
    np.save(inputs["mask"], np.zeros(COUNT + 1, dtype=np.bool_))

    with pytest.raises(LabelConversionError, match="mask length 6"):
        run(inputs)
    assert not inputs["output"].exists()


def test_rejects_wrong_source(inputs: dict[str, Path], tmp_path: Path) -> None:
    other = write_ply(tmp_path / "other.ply", marker="b")

    with pytest.raises(LabelConversionError, match="source checksum mismatch"):
        run(inputs, source_path=other)
    assert not inputs["output"].exists()


def test_rejects_manifest_count_that_disagrees_with_header(
    inputs: dict[str, Path], tmp_path: Path
) -> None:
    manifest = write_manifest(tmp_path / "wrong-count.json", inputs["source"], count=COUNT + 1)

    with pytest.raises(LabelConversionError, match="Gaussian count mismatch"):
        run(inputs, manifest_path=manifest)


def test_rejects_non_boolean_mask(inputs: dict[str, Path]) -> None:
    np.save(inputs["mask"], np.array([1, 0, 1, 0, 0], dtype=np.uint8))

    with pytest.raises(LabelConversionError, match="1-D Boolean"):
        run(inputs)


def test_never_reuses_an_output_directory(inputs: dict[str, Path]) -> None:
    inputs["output"].mkdir()

    with pytest.raises(LabelConversionError, match="already exists"):
        run(inputs)
    assert list(inputs["output"].iterdir()) == []


@pytest.mark.parametrize("object_id", [0, 65534])
def test_rejects_reserved_object_ids(inputs: dict[str, Path], object_id: int) -> None:
    with pytest.raises(LabelConversionError, match="object_id must be"):
        run(inputs, object_id=object_id)


def test_reads_vertex_count_from_header(tmp_path: Path) -> None:
    assert read_ply_vertex_count(write_ply(tmp_path / "x.ply", count=7)) == 7


def test_cli_reports_rejection(inputs: dict[str, Path]) -> None:
    np.save(inputs["mask"], np.zeros(COUNT + 1, dtype=np.bool_))

    result = RUNNER.invoke(
        app,
        [
            "convert-mask",
            "--mask", str(inputs["mask"]),
            "--source", str(inputs["source"]),
            "--manifest", str(inputs["manifest"]),
            "--output", str(inputs["output"]),
            "--object-id", "1",
            "--object-name", "yellow bowl",
            "--method", "gaussian-grouping",
            "--method-version", "class-108-threshold-0.3",
        ],
    )  # fmt: skip

    assert result.exit_code == 1
    assert "nothing was written" in result.stdout

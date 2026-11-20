"""Compare the exporter with the upstream classifier on known inputs."""

import importlib.util
import json
import subprocess
import sys
from pathlib import Path

import numpy as np
import pytest
import torch
from plyfile import PlyData, PlyElement

SCRIPT = Path(__file__).with_name("export_labels.py")
spec = importlib.util.spec_from_file_location("gg_export", SCRIPT)
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)


@pytest.fixture
def inputs(tmp_path):
    # Spatial and property orders differ to make accidental reordering observable.
    names = ["x", "y", "z"] + [f"obj_dc_{i}" for i in reversed(range(16))]
    rows = np.zeros(5, dtype=[(name, "f4") for name in names])
    rows["x"] = [9, -3, 4, 0, 1]
    rows["obj_dc_0"] = [2, -2, 0, 1, -1]
    rows["obj_dc_15"] = [0, 0, 4, -1, 2]
    ply = tmp_path / "source.ply"
    PlyData([PlyElement.describe(rows, "vertex")], byte_order=">").write(ply)
    classifier = torch.nn.Conv2d(16, 3, 1)
    with torch.no_grad():
        classifier.weight.zero_()
        classifier.bias.zero_()
        classifier.weight[0, 0] = 1
        classifier.weight[1, 0] = -1
        classifier.weight[2, 15] = 1
    checkpoint = tmp_path / "classifier.pth"
    torch.save(classifier.state_dict(), checkpoint)
    return ply, checkpoint, classifier, rows


def test_cli_matches_upstream_classifier(inputs, tmp_path):
    ply, checkpoint, classifier, rows = inputs
    out = tmp_path / "result"
    subprocess.run(
        [
            sys.executable,
            str(SCRIPT),
            "--ply",
            str(ply),
            "--classifier",
            str(checkpoint),
            "--output",
            str(out),
            "--select-id",
            "0",
            "--select-id",
            "2",
            "--chunk-size",
            "2",
        ],
        check=True,
        capture_output=True,
    )
    # Upstream applies Conv2d to [channels, N, 1].
    features = np.stack([rows[f"obj_dc_{i}"] for i in range(16)]).astype("float32")
    with torch.no_grad():
        probabilities = classifier(torch.from_numpy(features[:, :, None])).softmax(0)
    expected_mask = (probabilities[[0, 2], :, 0] > 0.3).any(0).numpy()
    np.testing.assert_array_equal(np.load(out / "native_id.npy"), [0, 1, 2, 0, 2])
    np.testing.assert_allclose(
        np.load(out / "confidence.npy"), probabilities.max(0).values[:, 0], rtol=1e-6
    )
    np.testing.assert_array_equal(np.load(out / "mask.npy"), expected_mask)
    report = json.loads((out / "report.json").read_text())
    assert report["class_histogram"] == [2, 1, 2]
    assert report["selection"]["selected_count"] == int(expected_mask.sum())


def test_chunk_size_preserves_results(inputs, tmp_path):
    ply, checkpoint, _, _ = inputs
    for chunk in (1, 100):
        module.export_labels(ply, checkpoint, tmp_path / str(chunk), chunk_size=chunk)
    np.testing.assert_array_equal(
        np.load(tmp_path / "1/native_id.npy"), np.load(tmp_path / "100/native_id.npy")
    )
    np.testing.assert_allclose(
        np.load(tmp_path / "1/confidence.npy"), np.load(tmp_path / "100/confidence.npy")
    )


def test_all_classes_without_target_mask(inputs, tmp_path):
    ply, checkpoint, _, _ = inputs
    out = tmp_path / "all"
    report = module.export_labels(ply, checkpoint, out)
    assert np.load(out / "native_id.npy").dtype == np.int64
    assert np.load(out / "confidence.npy").dtype == np.float32
    assert not (out / "mask.npy").exists()
    assert report["selection"]["selected_count"] is None

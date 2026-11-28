import json
import subprocess
import sys
from pathlib import Path

import numpy as np
from analyze import find_candidates
from plyfile import PlyData, PlyElement


def test_only_small_distant_islands_are_candidates():
    # Anchor wins by Gaussian count, although the other object occupies more voxels.
    anchor = np.repeat([[0.1, 0.1, 0.1]], 20, axis=0)
    near = [[2.1, 0.1, 0.1]]
    far = [[10.1, 0.1, 0.1]]
    other_object = [[20.1, 0.1, 0.1], [21.1, 0.1, 0.1], [22.1, 0.1, 0.1]]
    points = np.vstack([anchor, near, far, other_object])
    candidates, components = find_candidates(points, 1, 3, 0.1)
    np.testing.assert_array_equal(np.flatnonzero(candidates), [21])
    assert components[0]["gaussian_count"] == 20
    assert components[0]["anchor"]


def test_face_connectivity_and_negative_voxels():
    points = np.array([[-1.1, 0, 0], [-0.1, 0, 0], [0.1, 1.1, 0]])
    candidates, components = find_candidates(points, 1, 0.5, 0.5)
    assert len(components) == 2  # Diagonal contact is not face adjacency.
    np.testing.assert_array_equal(candidates, [False, False, True])


def test_minimum_gap_protects_an_extended_island():
    points = np.array([[0, 0, 0]] * 20 + [[i + 0.1, 0, 0] for i in range(2, 10)])
    candidates, _ = find_candidates(points, 1, 3, 0.5)
    assert not candidates.any()  # Far centroid, but its closest center is nearby.


def test_empty_selection_and_single_component():
    candidates, components = find_candidates(np.empty((0, 3)), 1, 1, 1)
    assert len(candidates) == len(components) == 0
    candidates, components = find_candidates(np.array([[0, 0, 0], [0.1, 0, 0]]), 1, 0, 1)
    assert not candidates.any()
    assert len(components) == 1


def test_cli_preserves_inputs_and_full_scene_order(tmp_path):
    points = np.array(
        [(10, 0, 0), (99, 0, 0), (0, 0, 0), (0.1, 0, 0)],
        dtype=[("x", "f4"), ("y", "f4"), ("z", "f4")],
    )
    source = tmp_path / "source.ply"
    mask_path = tmp_path / "mask.npy"
    PlyData([PlyElement.describe(points, "vertex")]).write(source)
    mask = np.array([True, False, True, True])
    np.save(mask_path, mask)
    original_ply, original_mask = source.read_bytes(), mask_path.read_bytes()
    command = [
        sys.executable,
        str(Path(__file__).with_name("analyze.py")),
        "--ply",
        str(source),
        "--mask",
        str(mask_path),
        "--voxel-size",
        "1",
        "--min-distance",
        "3",
        "--max-fraction",
        "0.5",
    ]
    for preview in (False, True):
        output = tmp_path / str(preview)
        subprocess.run(
            command + ["--output", str(output)] + (["--write-preview"] if preview else []),
            check=True,
            capture_output=True,
            text=True,
        )
        np.testing.assert_array_equal(
            np.load(output / "candidate_mask.npy"), [True, False, False, False]
        )
        assert (output / "preview_mask.npy").exists() == preview
        if preview:
            np.testing.assert_array_equal(
                np.load(output / "preview_mask.npy"), [False, False, True, True]
            )
        report = json.loads((output / "report.json").read_text())
        assert report["candidate_count"] == 1
        assert report["retained_count"] == 2
    assert source.read_bytes() == original_ply
    assert mask_path.read_bytes() == original_mask

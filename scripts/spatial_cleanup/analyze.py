"""Report distant, small label islands without modifying the source mask."""

import argparse
import json
from pathlib import Path
from time import perf_counter

import numpy as np
from plyfile import PlyData
from scipy.sparse import coo_matrix
from scipy.sparse.csgraph import connected_components
from scipy.spatial import cKDTree


def find_candidates(points, voxel_size, min_distance, max_fraction):
    """Use face-connected voxels; measure island gaps between actual centers.

    Inputs are finite selected centers [M, 3] in source PLY units, positive
    voxel_size, nonnegative min_distance and max_fraction in [0, 1]. The largest
    component by Gaussian count is the anchor, not necessarily a semantic object.
    """
    if len(points) == 0:
        return np.zeros(0, dtype=bool), []

    voxels, inverse = np.unique(
        np.floor(points / voxel_size).astype(np.int64), axis=0, return_inverse=True
    )
    pairs = cKDTree(voxels).query_pairs(1, p=1, output_type="ndarray")
    graph = coo_matrix(
        (np.ones(len(pairs)), (pairs[:, 0], pairs[:, 1])), shape=(len(voxels), len(voxels))
    )
    component_count, voxel_labels = connected_components(graph, directed=False)
    labels = voxel_labels[inverse]
    counts = np.bincount(labels)
    anchor = int(counts.argmax())
    distances = cKDTree(points[labels == anchor]).query(points)[0]
    gaps = np.full(component_count, np.inf)
    np.minimum.at(gaps, labels, distances)
    candidate_components = (gaps >= min_distance) & (counts <= counts[anchor] * max_fraction)
    candidate_components[anchor] = False

    lower = np.full((component_count, 3), np.inf)
    upper = np.full((component_count, 3), -np.inf)
    np.minimum.at(lower, labels, points)
    np.maximum.at(upper, labels, points)
    components = [
        {
            "id": int(i),
            "gaussian_count": int(counts[i]),
            "anchor": bool(i == anchor),
            "min_distance_to_anchor": float(gaps[i]),
            "candidate": bool(candidate_components[i]),
            "bounds": {"min": lower[i].tolist(), "max": upper[i].tolist()},
        }
        for i in np.argsort(-counts, kind="stable")
    ]
    return candidate_components[labels], components


def bounds(points):
    return (
        {"min": points.min(axis=0).tolist(), "max": points.max(axis=0).tolist()}
        if len(points)
        else None
    )


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--ply", type=Path, required=True)
    parser.add_argument("--mask", type=Path, required=True, help="bool[N] in source PLY order")
    parser.add_argument("--voxel-size", type=float, default=0.02)
    parser.add_argument("--min-distance", type=float, default=0.1)
    parser.add_argument("--max-fraction", type=float, default=0.01)
    parser.add_argument("--output", type=Path, required=True, help="New run directory")
    parser.add_argument(
        "--write-preview", action="store_true", help="Also write a proposed mask copy"
    )
    args = parser.parse_args()
    started = perf_counter()
    vertices = PlyData.read(args.ply)["vertex"].data
    mask = np.load(args.mask)
    points = np.column_stack([vertices[axis][mask] for axis in "xyz"])
    selected_candidates, components = find_candidates(
        points, args.voxel_size, args.min_distance, args.max_fraction
    )
    candidates = np.zeros(len(vertices), dtype=bool)
    candidates[mask] = selected_candidates
    args.output.mkdir(parents=True, exist_ok=False)
    np.save(args.output / "candidate_mask.npy", candidates)
    if args.write_preview:
        np.save(args.output / "preview_mask.npy", mask & ~candidates)
    report = {
        "source_ply": str(args.ply),
        "source_mask": str(args.mask),
        "gaussian_count": len(vertices),
        "parameters": {
            "voxel_size": args.voxel_size,
            "adjacency": 6,
            "min_distance": args.min_distance,
            "max_fraction": args.max_fraction,
        },
        "selected_count": int(mask.sum()),
        "component_count": len(components),
        "candidate_component_count": sum(c["candidate"] for c in components),
        "candidate_count": int(candidates.sum()),
        "retained_count": int(mask.sum() - candidates.sum()),
        "before_bounds": bounds(points),
        "preview_bounds": bounds(points[~selected_candidates]),
        "preview_written": args.write_preview,
        "runtime_seconds": perf_counter() - started,
        "components": components,
    }
    (args.output / "report.json").write_text(json.dumps(report, indent=2) + "\n")
    print(json.dumps({k: v for k, v in report.items() if k != "components"}, indent=2))


if __name__ == "__main__":
    main()
